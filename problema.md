# Relatório de Incidentes: Instabilidade na Integração com o Yahoo Finance (yfinance)

## Contexto do Problema
O **Candez Quant Platform** vinha enfrentando falhas severas de comunicação nos módulos que dependem de dados históricos de mercado (Long & Short, Opções e Momentum), resultando em retornos vazios no Frontend ou erros `500 Internal Server Error`.

Após análise dos logs em ambiente de produção (Render) e testes de execução local, identificou-se que o problema central não residia na lógica matemática dos motores, mas sim nas restrições de rede e mecanismos anti-bot recentes implementados pelo Yahoo Finance, além de incompatibilidades do ambiente de hospedagem.

## 1. Bloqueio por Limite de Requisições (Rate Limit 429)
O Yahoo Finance (via biblioteca `yfinance`) adotou uma postura muito agressiva contra extrações em massa de dados. 
* **O que estava acontecendo:** Módulos como o Scanner L&S e o Radar de Volatilidade solicitavam o download do histórico do IBRX-100 de forma simultânea. A biblioteca `yfinance` utiliza multithreading por padrão para baixar vários ativos ao mesmo tempo. 
* **Consequência:** Os servidores do Yahoo detectavam a rajada de conexões provenientes do mesmo IP (o IP do Render) e aplicavam um bloqueio instantâneo. Nos logs, isso se refletia como `YFRateLimitError('Too Many Requests. Rate limited.')` e `HTTP Error 401: Unauthorized (Invalid Crumb)`.
* **Solução Aplicada:** Modificamos o wrapper de download (`backend/core/yf_setup.py`) para forçar `threads=False`. Isso obriga o sistema a baixar a cotação de cada ativo de forma estritamente sequencial, reduzindo o estresse no servidor destino e evitando bloqueios. Adicionalmente, implementamos um pequeno atraso (`time.sleep(0.5)`) entre chamadas para suavizar a taxa de acesso.

## 2. Incompatibilidade de Cache de Sessão (requests-cache vs curl_cffi)
* **O que estava acontecendo:** Anteriormente, o backend utilizava a biblioteca `requests_cache` para interceptar as chamadas web e guardar os dados em um banco SQLite local (`http_cache.sqlite`), poupando requisições repetidas. No entanto, atualizações recentes do `yfinance` passaram a exigir a biblioteca `curl_cffi` sob o capô para contornar verificações de segurança do Yahoo (os "Crumbs"). O `requests_cache` é **incompatível** com as sessões geradas pelo `curl_cffi`.
* **Consequência:** Qualquer tentativa de injetar o cache de requisição causava a exceção fatal: `YFDataException: request_cache sessions don't work with curl_cffi`. Isso quebrava imediatamente a inicialização do módulo, derrubando os endpoints.
* **Solução Aplicada:** Removemos completamente a dependência do `requests_cache` e seu arquivo SQLite associado do projeto (`requirements.txt` e `yf_setup.py`). Em substituição, mantivemos e aprimoramos um cache em memória RAM (`_cache = {}` no Python) que guarda os DataFrames retornados pelo Yahoo por 1 hora, entregando a mesma velocidade de resposta do Frontend sem interferir nos mecanismos internos do `yfinance`.

## 3. Erro de Permissão de Arquivos no Render (TzCache)
* **O que estava acontecendo:** O `yfinance` tenta por padrão criar uma pasta de cache de fusos horários (Timezones) no diretório temporário do sistema operacional (ex: `/opt/render/.cache/py-yfinance`). O ambiente restrito do Render não concedia permissões de sobrescrita adequadas para esse diretório, causando falhas concorrentes (`[Errno 17] File exists`).
* **Consequência:** Embora não fosse um erro totalmente fatal para a aplicação, poluía os logs e poderia gerar travamentos no escalonamento dos *Workers* do FastAPI.
* **Solução Aplicada:** Forçamos o diretório de cache do `yfinance` para `/tmp/yfinance_cache`, uma pasta temporária padrão do Linux onde temos garantias de permissões completas de leitura/escrita.

## 4. Avisos de Depreciação no Pandas (FutureWarnings)
* **O que estava acontecendo:** O motor de Arbitragem (`engine_ls.py`) utilizava o método `.fillna(method='bfill')`, que foi marcado para ser removido em versões futuras da biblioteca `pandas`.
* **Consequência:** Geração de ruído visual nos logs da aplicação ("FutureWarning: Series.fillna with 'method' is deprecated").
* **Solução Aplicada:** Atualizamos a sintaxe do pandas para a forma moderna, substituindo por `.bfill()` e `.ffill()`, garantindo que o código se mantenha resiliente em futuras atualizações das dependências matemáticas.

## Próximos Passos
Os commits com as devidas correções já foram construídos e adicionados ao repositório local. O administrador do sistema deve efetuar o comando `git push` no diretório `backend/` para desencadear um novo processo de Build & Deploy no Render. Uma vez online, o sistema passará a buscar os ativos com responsabilidade (sequencialmente), restabelecendo os serviços quantitativos.