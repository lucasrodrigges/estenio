# Estenio — Context

## Glossary

- **Estenio** — Aplicação CLI interativa, passo a passo, para download de mídia de plataformas online. Versão 0.2.0.
- **Source** — Plataforma de origem suportada: YouTube ou Instagram.
- **Download type** — Depende da Source. YouTube: Audio (só áudio) ou Video (MP4 com áudio). Instagram: Reels (link único de um reel) ou Stories (link do perfil do usuário).
- **Format** — Formato do arquivo de saída. YouTube áudio: WAV ou MP3. YouTube vídeo: MP4. Instagram: MP4 (fixo, sem escolha de formato).
- **Step** — Um prompt interativo no fluxo. O usuário avança sequencialmente.
- **yt-dlp** — Engine externa usada via subprocess para extração e conversão. Nunca importada como biblioteca.
- **ffmpeg** — Ferramenta externa usada pelo yt-dlp para merge de faixas e conversão de formatos.
- **Output directory** — Diretório onde os arquivos são salvos. Padrão: diretório atual de onde `estenio` foi invocado.
- **Pre-flight check** — Na inicialização, verifica se `yt-dlp` e `ffmpeg` estão instalados. Se faltar, mostra o comando e sai.
- **URL validation** — Validação simples (não-vazio) para todas as URLs. O yt-dlp é responsável por validar o formato e reportar erros, que o ERROR_MAP traduz.
- **YouTube playlist** — Coleção de vídeos identificada por uma referência `list` em um link do YouTube.
- **Hybrid YouTube link** — Link que identifica simultaneamente um vídeo específico e uma YouTube playlist. Nesse caso, o usuário escolhe entre baixar somente o vídeo indicado ou a playlist completa.
- **Playlist-only YouTube link** — Link que identifica uma YouTube playlist sem indicar um vídeo específico; representa diretamente a playlist completa.
- **YouTube download scope** — Alcance de um download iniciado por um Hybrid YouTube link: somente o vídeo indicado ou a playlist completa. O vídeo único é a escolha padrão.
- **YouTube channel link** — Link oficial de canal nos formatos `@handle`, `/channel/ID`, `/c/nome` ou `/user/nome`; pode representar todos os vídeos do canal.
- **YouTube channel section link** — YouTube channel link direcionado a uma seção como `/videos`, `/shorts` ou `/streams`; representa todos os itens daquela seção, não necessariamente todos os vídeos do canal.
- **Channel download confirmation** — Confirmação obrigatória antes de baixar um YouTube channel link ou YouTube channel section link. Continuar e baixar é a escolha padrão; cancelar retorna ao início do fluxo sem download.
- **Instagram auth** — Sempre usa `yt-dlp --cookies-from-browser <navegador>` nos downloads do Instagram. O navegador é detectado automaticamente na ordem: `$BROWSER` → `xdg-settings get default-web-browser` → fallback firefox → chrome → chromium. Se nenhum for encontrado, erro claro.
- **Browser check timing** — A detecção do navegador acontece no momento do download (não no startup). Se o usuário só usa YouTube, nunca vê o assunto.
- **Download progress** — O progresso nativo do yt-dlp é mostrado diretamente no terminal, sem modificações.
- **Reels command** — Comando mínimo: `yt-dlp --cookies-from-browser <browser> <url>`. Sem flags de formato — o yt-dlp escolhe a melhor qualidade e o Reels já é MP4 nativo.
- **Error handling** — Erros do yt-dlp são capturados, traduzidos para mensagens em português, e o usuário volta ao input de URL. O ERROR_MAP cobre padrões do YouTube e do Instagram (perfil privado, story expirado, exigência de login, link inválido).
- **Flow** — Steps: Source → Type (depende da Source) → Format (condicional do Type) → URL → confirmação/escopo condicional → Download. Ao concluir, volta ao step 1. YouTube: Type=Video → Format pulado (MP4 implícito); Type=Audio → Format pergunta MP3 ou WAV; Hybrid YouTube link → pergunta YouTube download scope; YouTube channel link → Channel download confirmation. Instagram: step Format e os prompts condicionais de YouTube são sempre pulados (MP4 implícito) — Reels e Stories só produzem vídeo MP4.
- **Stories command** — Mesmo comando mínimo do Reels: `yt-dlp --cookies-from-browser <browser> <url>`. O yt-dlp detecta o path `/stories/` e ativa o extrator correto, baixando todos os stories ativos como MP4 individuais.
- **URL prompt** — O texto do prompt de URL adapta-se à Source e ao Type. YouTube: "Link do YouTube:". Instagram Reels: "Link do Reels:". Instagram Stories: "Link do perfil:".
- **Stories URL conversion** — Se o usuário colar um link de perfil comum (`instagram.com/fulano`), o Estenio converte internamente para a URL de stories (`instagram.com/stories/fulano/`) antes de chamar o yt-dlp. Transparente para o usuário.
