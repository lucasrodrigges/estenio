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

A instalação é feita exclusivamente pelo terminal. O script detecta o sistema, verifica o Python, configura um ambiente isolado e instala ffmpeg e as dependências necessárias quando preciso.

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/lucasrodrigges/estenio/main/scripts/install.sh | bash
```

### Windows (PowerShell como Administrador)

```powershell
irm https://raw.githubusercontent.com/lucasrodrigges/estenio/main/scripts/install.ps1 | iex
```

Depois, abra um novo terminal e execute:

```bash
estenio
```

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
