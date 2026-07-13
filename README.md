<!-- teste build -->

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

## 🚀 Instalação

**Baixe o executável pronto para o seu sistema e execute — zero configuração.**

| Plataforma | Download |
|------------|----------|
| 🐧 **Linux** | [estenio-linux](https://github.com/lucasrodrigges/estenio/releases/latest/download/estenio-linux) |
| 🍎 **macOS** | [estenio-macos](https://github.com/lucasrodrigges/estenio/releases/latest/download/estenio-macos) |
| 🪟 **Windows** | [estenio-windows.exe](https://github.com/lucasrodrigges/estenio/releases/latest/download/estenio-windows.exe) |

### Linux / macOS

```bash
# Dê permissão de execução e execute
chmod +x estenio-linux
./estenio-linux
```

### Windows

Basta executar o arquivo `.exe` — dê um duplo clique ou execute pelo terminal:

```powershell
.\estenio-windows.exe
```

> 💡 **Dica:** No Linux/macOS, mova o binário para `~/.local/bin/` para poder executar `estenio` de qualquer lugar:
> ```bash
> mv estenio-linux ~/.local/bin/estenio
> estenio
> ```

---

## 🛠 Instalação via Script (alternativa)

Se preferir instalar a partir do código-fonte com um script que configura tudo automaticamente:

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/lucasrodrigges/estenio/main/scripts/install.sh | bash
```

### Windows (PowerShell como Administrador)

```powershell
irm https://raw.githubusercontent.com/lucasrodrigges/estenio/main/scripts/install.ps1 | iex
```

O script detecta automaticamente seu sistema e instala Python, ffmpeg e todas as dependências necessárias.

---

### Instagram: login no navegador

Para baixar do Instagram, você precisa estar logado na sua conta pelo navegador (Firefox ou Chrome). O Estenio detecta automaticamente e usa seus cookies — você não precisa fazer nada além de estar logado.

---

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
