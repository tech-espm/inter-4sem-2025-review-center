# Projeto Interdisciplinar IV - Sistemas de Informação ESPM

<p align="center">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>

# Review Center

### 2025-02

## Visão Geral

Este projeto teve como ponto de partida a aplicação prática da ferramenta Selenium, com o objetivo de realizar raspagem de dados em um ambiente real. A proposta consistiu em automatizar a navegação em páginas do site Metacritic para extrair informações estruturadas sobre jogos, simulando o comportamento de um usuário real no navegador.

Durante essa etapa, foram coletados dados como nome do jogo, publisher, gênero, ano de lançamento, Metascore, avaliações da crítica e dos usuários, além da classificação indicativa. Após a coleta, os dados passaram por processos de tratamento e organização em Python, sendo então armazenados em um banco de dados SQL para posterior utilização.

## Participantes

- [José Longo Neto](https://github.com/Jose-Longo-A)
- [Enzo Malagoli](https://github.com/EnzoMalagoli)
- [Pablo Dimitrof](https://github.com/PabloDimitrof)
- [Pedro Maricate](https://github.com/PedroMaricate)
- [Martim Ponzio](https://github.com/martimponzio)
- [Eduardo Gul](https://github.com/eduardogd09)

## Objetivos do Projeto

A partir da etapa de raspagem, surgiu o Review Center, uma plataforma desenvolvida para organizar, analisar e visualizar os dados coletados. O objetivo do projeto é transformar informações brutas em análises claras e acessíveis, permitindo comparações entre a percepção da crítica especializada e do público, além da identificação de padrões relacionados a publishers, gêneros e períodos de lançamento.

O Review Center disponibiliza essas análises por meio de uma aplicação web com tabelas, filtros e gráficos interativos, facilitando a exploração dos dados e a geração de insights sobre o mercado de jogos digitais.

## Configuração do Projeto

- Python 3.9 ou superior
- Google Chrome instalado
- ChromeDriver compatível com a versão do navegador
- Banco de dados SQL (MySQL ou PostgreSQL)
- Git

## Criação e Ativação do venv

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```
.venv\Scripts\activate
python app.py
```

## Mais Informações

https://flask.palletsprojects.com/en/3.0.x/quickstart/
https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

# Licença

Este projeto é licenciado sob a [MIT License](https://github.com/tech-espm/inter-4sem-2025-volumetria-de-presenca/blob/main/LICENSE).

<p align="right">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo-si-512.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>
