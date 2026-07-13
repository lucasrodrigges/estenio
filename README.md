# Estenio

CLI interativa para baixar vídeos e áudio do YouTube, Reels e Stories do Instagram — sem flags, sem complicação.

```
$ estenio
┌──────────────────────────┐
│         Estenio          │
│  v0.2.0 — YT + Instagram │
└──────────────────────────┘
? O que você quer baixar? Instagram
? Tipo de download: Reels (link único)
? Link do Reels: https://...
✅ Download concluído!
```

## Pré-requisitos

| Dependência | Como instalar |
|------------|---------------|
| **Python 3.10+** | [python.org](https://python.org) ou `sudo apt install python3` |
| **pip** | Já vem com Python ≥ 3.4 |
| **yt-dlp** | `pip install yt-dlp` |
| **ffmpeg** | `sudo apt install ffmpeg` (Ubuntu/Debian) \| `brew install ffmpeg` (macOS) \| [ffmpeg.org](https://ffmpeg.org) (Windows) |

### Instagram: login no navegador

Para baixar do Instagram, você precisa estar logado na sua conta pelo navegador (Firefox ou Chrome). O Estenio detecta automaticamente e usa seus cookies — você não precisa fazer nada além de estar logado.

## Instalação

### Opção 1: Instalar do GitHub (recomendado)

```bash
# Clone o repositório
git clone https://github.com/lucasrodrigges/estenio.git
cd estenio

# Instale o pacote
pip install .
```

### Opção 2: Instalar em modo desenvolvimento

```bash
git clone https://github.com/lucasrodrigges/estenio.git
cd estenio

# Instala com symlink — alterações no código refletem na hora
pip install -e .
```

### Verificando a instalação

```bash
estenio
```

Se o comando não for encontrado, verifique se o diretório de scripts do Python está no seu PATH:

```bash
# Linux/macOS — adicione ao ~/.bashrc ou ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Dica: ambiente virtual (opcional)

Recomendado para manter as dependências isoladas:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install .
```

### Desinstalar

```bash
pip uninstall estenio
```

## Uso

```bash
estenio
```

Siga os prompts. Ao final do download, você pode baixar outro conteúdo ou `Ctrl+C` para sair.

## Tipos de download

### YouTube

| Tipo | Resultado |
|------|-----------|
| Apenas áudio | Arquivo MP3 ou WAV (melhor qualidade) |
| Vídeo | Arquivo MP4 com áudio (melhor qualidade disponível) |
| Ambos | Vídeo MP4 (sem áudio) + Áudio MP3/WAV — dois arquivos |

### Instagram

| Tipo | URL esperada | Resultado |
|------|-------------|-----------|
| Reels | Link do reel (`instagram.com/reel/...`) | Arquivo MP4 |
| Stories | Link do perfil (`instagram.com/fulano`) | Todos os stories ativos como MP4 individuais |
