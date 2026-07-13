# Estenio — Instalador Multiplataforma Autossuficiente

## Contexto

O Estenio é uma CLI interativa em Python que baixa vídeos/áudio do YouTube e Instagram. Hoje, o usuário precisa instalar manualmente:

- Python 3.10+
- yt-dlp (via pip)
- ffmpeg (via apt/brew/download manual)
- Dependências Python (questionary, rich)

Para um usuário leigo, isso é uma barreira alta — especialmente no Windows, onde instalar ffmpeg e colocar no PATH é complexo. O objetivo é que o usuário execute **um único comando** (ou baixe um único executável) e tudo funcione.

## Abordagem

**Duas frentes complementares:**

1. **Executável standalone com PyInstaller** — empacota Python + yt-dlp + todas as dependências Python em um binário único por plataforma. O ffmpeg é embutido como recurso (data file) e extraído em runtime. Distribuído via GitHub Releases com builds automatizados por GitHub Actions.

2. **Script de instalação universal** — um script bash/PowerShell que detecta a plataforma, instala o que falta (Python, ffmpeg) e configura o ambiente. Serve como alternativa para quem prefere rodar a partir do fonte ou não confia em binários.

**Por que PyInstaller como abordagem principal:**
- Usuário leigo baixa **um arquivo** e executa — zero configuração
- yt-dlp é código Python puro, empacota perfeitamente
- ffmpeg é o único binário nativo; embutimos os binários de cada plataforma como `data_files`
- GitHub Actions gera os 3 binários automaticamente a cada release

## O que NÃO muda

- O código-fonte Python do Estenio continua igual (main.py, steps.py, downloader.py, checks.py)
- A CLI interativa (questionary) continua a mesma
- A experiência de uso é idêntica — só a instalação muda

## Arquivos a modificar/criar

| Arquivo | Ação | Propósito |
|---------|------|-----------|
| `pyproject.toml` | Modificar | Adicionar `pyinstaller` como dev dependency; declarar `data_files` para ffmpeg |
| `src/estenio/__init__.py` | Modificar | Adicionar `_get_ffmpeg_path()` — resolve caminho do ffmpeg bundled vs sistema |
| `src/estenio/checks.py` | Modificar | `check_dependencies()` usa ffmpeg bundled se disponível, fallback para PATH |
| `src/estenio/downloader.py` | Modificar | Adicionar `FFMPEG_PATH` ao ambiente antes de chamar yt-dlp |
| `estenio.spec` | Criar | Configuração do PyInstaller (entry point, hidden imports, data files) |
| `scripts/install.sh` | Criar | Script de instalação autossuficiente para Linux/macOS |
| `scripts/install.ps1` | Criar | Script de instalação autossuficiente para Windows |
| `scripts/bundle-ffmpeg.sh` | Criar | Script auxiliar para baixar binários ffmpeg de cada plataforma |
| `.github/workflows/release.yml` | Criar | CI/CD: build multiplataforma + GitHub Release |

## Reuso

| Recurso existente | Localização | Como reusar |
|-------------------|-------------|-------------|
| `check_dependencies()` | `src/estenio/checks.py` | Estender para checar ffmpeg bundled antes do sistema |
| `Dependency` dataclass | `src/estenio/checks.py` | Mantém a estrutura, adiciona flag `bundled: bool` |
| `build_command()` | `src/estenio/downloader.py` | Não muda — continuamos chamando yt-dlp via subprocess |
| `translate_error()` | `src/estenio/downloader.py` | Intocado |
| Estrutura de entry point `main()` | `src/estenio/main.py` | Intocada |

## Steps — PyInstaller (principal)

- [ ] **1. Adicionar `pyinstaller` como dev dependency no `pyproject.toml`**
  ```toml
  [project.optional-dependencies]
  dev = ["pytest>=8.0.0", "pyinstaller>=6.0.0"]
  ```

- [ ] **2. Criar script `scripts/bundle-ffmpeg.sh` para baixar binários ffmpeg**
  - Baixa builds estáticas oficiais do ffmpeg (https://ffmpeg.org/download.html) ou via `yt-dlp -g` para obter binários confiáveis
  - Organiza em `src/estenio/bin/ffmpeg-linux`, `src/estenio/bin/ffmpeg-macos`, `src/estenio/bin/ffmpeg-windows.exe`
  - Gera checksums para verificação

- [ ] **3. Modificar `src/estenio/__init__.py` — função `_get_ffmpeg_path()`**
  ```python
  def _get_ffmpeg_path() -> str | None:
      """Return path to bundled ffmpeg, or None if not bundled."""
      import sys
      import os
      from pathlib import Path
      
      # When running from PyInstaller bundle
      if getattr(sys, 'frozen', False):
          base = Path(sys._MEIPASS)
      else:
          base = Path(__file__).parent
      
      # Platform-specific binary name
      if sys.platform == 'win32':
          binary = 'ffmpeg-windows.exe'
      elif sys.platform == 'darwin':
          binary = 'ffmpeg-macos'
      else:
          binary = 'ffmpeg-linux'
      
      candidate = base / 'bin' / binary
      if candidate.exists():
          os.chmod(candidate, 0o755)  # ensure executable
          return str(candidate)
      return None
  ```

- [ ] **4. Modificar `src/estenio/checks.py`**
  - `check_dependencies()` verifica ffmpeg bundled primeiro (`_get_ffmpeg_path()`), depois fallback para `shutil.which("ffmpeg")`
  - Adicionar campo `bundled: bool = False` no `Dependency` dataclass
  - Ajustar mensagem de erro para não sugerir instalação manual quando bundled está disponível

- [ ] **5. Modificar `src/estenio/downloader.py`**
  - Antes de chamar `subprocess.run(cmd, ...)`, injetar `FFMPEG_PATH` no ambiente:
    ```python
    env = os.environ.copy()
    ffmpeg_path = _get_ffmpeg_path()
    if ffmpeg_path:
        env['PATH'] = str(Path(ffmpeg_path).parent) + os.pathsep + env.get('PATH', '')
    ```
  - Passar `env=env` para `subprocess.run()`

- [ ] **6. Criar `estenio.spec` do PyInstaller**
  ```python
  # -*- mode: python ; coding: utf-8 -*-
  a = Analysis(
      ['src/estenio/main.py'],
      pathex=[],
      binaries=[],
      datas=[('src/estenio/bin', 'estenio/bin')],
      hiddenimports=['questionary', 'rich', 'yt_dlp'],
      hookspath=[],
      hooksconfig={},
      runtime_hooks=[],
      excludes=[],
      noarchive=False,
  )
  pyz = PYZ(a.pure)
  exe = EXE(
      pyz,
      a.scripts,
      a.binaries,
      a.datas,
      name='estenio',
      debug=False,
      bootloader_ignore_signals=False,
      strip=False,
      upx=True,
      upx_exclude=[],
      runtime_tmpdir=None,
      console=True,
      disable_windowed_traceback=False,
      argv_emulation=False,
      target_arch=None,
      codesign_identity=None,
      entitlements_file=None,
  )
  ```

- [ ] **7. Criar `.github/workflows/release.yml`**
  - Triggers: push de tag `v*` ou workflow_dispatch
  - 3 jobs paralelos: `build-linux`, `build-macos`, `build-windows`
  - Cada job:
    1. Checkout do código
    2. Setup Python 3.10+
    3. `scripts/bundle-ffmpeg.sh` (ou equivalente inline)
    4. `pip install -e ".[dev]"`
    5. `pyinstaller estenio.spec`
    6. Upload do artefato (`dist/estenio` ou `dist/estenio.exe`)
  - Job final `release`: baixa os 3 artefatos, cria GitHub Release com changelog

- [ ] **8. Atualizar `README.md`**
  - Nova seção "Instalação Rápida" com links diretos para download dos binários
  - Instruções: "Baixe o arquivo para seu sistema, execute, pronto"
  - Manter instruções de instalação via pip para desenvolvedores

## Steps — Script de instalação (alternativo)

- [ ] **9. Criar `scripts/install.sh` (Linux/macOS)**
  - Detecta SO (Linux distro ou macOS)
  - Verifica Python 3.10+; se ausente, sugere instalação (não instala automaticamente por segurança)
  - Verifica ffmpeg; se ausente, instala via `apt` (Ubuntu/Debian), `dnf` (Fedora), `pacman` (Arch), ou `brew` (macOS)
  - Cria virtualenv, instala dependências Python + yt-dlp + estenio
  - Cria symlink `estenio` em `~/.local/bin/`
  - Adiciona ao PATH se necessário

- [ ] **10. Criar `scripts/install.ps1` (Windows)**
  - Verifica Python 3.10+; se ausente, baixa e instala do python.org (modo silencioso)
  - Verifica ffmpeg; se ausente, baixa build estática e extrai, adiciona ao PATH do usuário
  - Cria virtualenv, instala dependências
  - Cria atalho no Menu Iniciar ou script `.bat` no PATH

## Steps — Testes e verificação

- [ ] **11. Adicionar teste para `_get_ffmpeg_path()`**
  - Testa modo bundled (simula `sys.frozen` e `sys._MEIPASS`)
  - Testa fallback para PATH do sistema
  - Testa permissões de execução no Linux/macOS

- [ ] **12. Testar build PyInstaller localmente (Linux)**
  ```bash
  pip install pyinstaller
  bash scripts/bundle-ffmpeg.sh
  pyinstaller estenio.spec
  ./dist/estenio   # deve rodar com zero dependências externas
  ```

## Verificação

1. **Linux**: `./dist/estenio` em um sistema limpo (Docker Ubuntu sem Python/ffmpeg) — deve funcionar
2. **macOS**: `./dist/estenio` em um Mac sem ffmpeg instalado — deve funcionar
3. **Windows**: `dist\estenio.exe` em um Windows limpo — deve funcionar
4. **Script install.sh**: rodar em VM limpa Ubuntu/Debian — deve instalar tudo e deixar funcional
5. **Script install.ps1**: rodar em VM Windows limpa — deve instalar tudo
6. **CI**: push de tag `v0.3.0` → GitHub Actions gera 3 binários → Release criado com todos os assets

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Binário ffmpeg grande (~80 MB) | Compactação UPX no PyInstaller; opção de download sob demanda no primeiro uso |
| yt-dlp atualiza frequentemente | O bundled yt-dlp funciona; o usuário pode opcionalmente ter yt-dlp no PATH que terá precedência |
| Falsos positivos de antivírus no Windows (PyInstaller) | Assinar binário com code signing certificate (futuro); instruir usuário sobre falso positivo |
| Cookies do navegador no Windows com PyInstaller | `--cookies-from-browser` do yt-dlp funciona normalmente — acessa os cookies do Chrome/Firefox no filesystem |
| Permissões do ffmpeg bundled no macOS (quarentena/Gatekeeper) | Instrução para `xattr -d com.apple.quarantine` ou usar `codesign` |
