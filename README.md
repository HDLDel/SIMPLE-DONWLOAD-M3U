# M3U VOD Downloader

Um programa em Python com interface gráfica para baixar vídeos de listas M3U. Especialmente útil para download de séries, filmes, novelas e outros conteúdos VOD (Video on Demand) disponíveis em listas M3U.

## Funcionalidades

- Interface gráfica amigável usando Tkinter
- Suporte para listas M3U locais e remotas (URLs)
- Download individual ou em sequência de vídeos selecionados
- Organização automática em pastas por conteúdo e temporada
- Barra de progresso em tempo real
- Exibição da velocidade de download
- Suporte para retomada de downloads interrompidos
- Filtro de busca por nome
- Filtro por categoria
- Marcação de múltiplos vídeos para download
- Botão para cancelar downloads em andamento

## Requisitos

### Python
- Python 3.8 ou superior

### Bibliotecas Python
Todas as bibliotecas necessárias estão listadas no arquivo `requirements.txt`:
```
requests
unidecode
```

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências usando pip:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Execute o programa:
```bash
python m3u_vod_downloader.py
```

2. Na interface do programa:

### Carregando uma Lista M3U
- Cole a URL da lista M3U no campo de texto
- Ou use o botão "Carregar Arquivo M3U" para carregar um arquivo local
- Clique em "Carregar" para processar a lista

### Navegando e Filtrando
- Use o campo de busca para filtrar por nome
- Use o combobox de categorias para filtrar por categoria
- A lista mostrará o total de vídeos e quantos estão sendo exibidos após os filtros

### Baixando Vídeos
1. Marque os vídeos que deseja baixar clicando na caixa de seleção
2. Escolha a pasta de destino usando o botão "Selecionar Pasta"
3. Clique em "Download Selected" para iniciar o download
4. O progresso será mostrado na barra inferior
5. Use o botão "Cancelar Download" para interromper downloads em andamento

### Organização dos Arquivos
O programa organiza automaticamente os downloads:
- Cria uma pasta para cada série/filme/novela
- Para séries e novelas, cria subpastas por temporada
- Nomeia os arquivos de forma limpa e organizada

## Estrutura de Pastas
```
Pasta de Download/
├── Nome da Série/
│   ├── Temporada 1/
│   │   ├── Episódio 1.mp4
│   │   └── Episódio 2.mp4
│   └── Temporada 2/
│       └── Episódio 1.mp4
└── Nome do Filme/
    └── Nome do Filme.mp4
```

## Recursos Técnicos

### Tratamento de Downloads
- Suporte para retomada de downloads interrompidos
- Verificação de arquivos já baixados
- Tratamento de timeouts e erros de conexão
- Tentativas automáticas em caso de falha
- Limpeza automática de arquivos parciais em caso de erro

### Processamento de Nomes
- Remoção de caracteres especiais
- Normalização de acentos
- Identificação automática de temporadas
- Criação de estrutura de pastas adequada

## Solução de Problemas

### Downloads Lentos
- Verifique sua conexão com a internet
- Verifique se o servidor de origem não está sobrecarregado
- Tente novamente em outro horário

### Erros de Conexão
- O programa tentará automaticamente reconectar
- Se persistir, verifique se a URL do vídeo ainda está válida
- Verifique se sua conexão está estável

### Arquivos Corrompidos
- Use o botão "Cancelar Download" para interromper
- Exclua o arquivo parcial
- Tente baixar novamente

## Limitações

- O programa baixa um vídeo por vez
- A velocidade de download depende do servidor de origem
- Alguns servidores podem ter limitações de banda
- Nem todas as listas M3U são compatíveis

## Notas de Segurança

- Use apenas com conteúdo que você tem permissão para baixar
- Não compartilhe URLs protegidas por senha
- Mantenha seu sistema e Python atualizados
- Use conexões seguras (HTTPS) quando possível

## Contribuindo

Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar correções
- Propor novas funcionalidades

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
