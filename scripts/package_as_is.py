"""Private export explicitly including local credentials, environment and logs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from package_share import ROOT, OUTPUT, COMMON, WEB, EXT, TEST_COMMON, guide


def main():
    OUTPUT.mkdir(exist_ok=True)
    runtime = []
    for directory in ['.venv', '.pytest_cache', '__pycache__']:
        runtime.extend(p for p in (ROOT/directory).rglob('*') if p.is_file())
    runtime.extend(ROOT.glob('*.log'))
    runtime.extend(p for p in [ROOT/'.streamlit/secrets.toml', ROOT/'.mailmate-extension-token'] if p.exists())
    extension_files = [p.relative_to(ROOT).as_posix() for p in (ROOT/'extension').rglob('*') if p.is_file()]
    archives = []
    try:
        for name, web, extension in [('webapp',True,False),('webapp-and-extension',True,True),('extension',False,True)]:
            archive = ZipFile(OUTPUT/f'{name}.zip', 'w', ZIP_DEFLATED, compresslevel=1)
            archives.append((name, archive))
            paths = COMMON + TEST_COMMON + ['requirements.txt', 'requirements-dev.txt'] + (WEB if web else []) + (EXT + extension_files if extension else [])
            if web and extension:
                # Preserve the complete source checkout and Git metadata.
                paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/'.git').rglob('*') if p.is_file())
                paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py'))
            for path in sorted(set(paths)):
                archive.write(ROOT/path, f'{name}/{path}')
            instructions = guide(web, extension)
            instructions = instructions.replace('your own Gemini API key', 'the included Gemini API configuration')
            instructions = instructions.replace('This package contains no API keys or tokens.', 'This private package includes the configured API key, old connection token, logs and Python environment.')
            instructions = instructions.replace('Copy-Item .streamlit\\secrets.toml.example .streamlit\\secrets.toml\n', '')
            instructions = instructions.replace('cp .streamlit/secrets.toml.example .streamlit/secrets.toml\n', '')
            instructions = instructions.replace('Replace `YOUR_API_KEY` with your\nown key.', 'The current key is already configured. Replace it only if you want to use a different account.')
            instructions = instructions.replace('The included model configuration is:', 'The template format is:')
            instructions = '**Private export: includes working credentials. Anyone receiving this archive can use the included Gemini key.**\n\n' + instructions
            instructions += '\n## Included environment\n\nThe `.venv` folder is included as requested. Python virtual environments are not portable across computers; if it does not launch, recreate it using the setup commands above. Existing credentials in `.streamlit/secrets.toml` are preserved.\n'
            archive.writestr(f'{name}/README.md', instructions)
        for index, path in enumerate(runtime):
            relative=path.relative_to(ROOT).as_posix()
            data=path.read_bytes()
            for name, archive in archives:
                archive.writestr(f'{name}/{relative}', data)
            if index and index % 3000 == 0:
                print(f'Included {index:,} runtime files in each archive', flush=True)
    finally:
        for _, archive in archives:
            archive.close()
    for name, _ in archives:
        target=OUTPUT/f'{name}.zip'
        with ZipFile(target) as archive:
            assert f'{name}/.streamlit/secrets.toml' in archive.namelist()
            assert f'{name}/.mailmate-extension-token' in archive.namelist()
            assert archive.testzip() is None
        print(f'Verified {target.name}: {target.stat().st_size() / 1024 / 1024:.1f} MB',flush=True)
    (OUTPUT/'README.md').write_text('# Private MailMate packages\n\nwebapp.zip, webapp-and-extension.zip, and extension.zip include configured credentials, tokens, Python environments and logs as requested. Each has setup instructions. Treat these archives as private. The old safe webapp snapshot remains at ../webapp-mailmate.zip.\n',encoding='utf-8')


if __name__ == '__main__':
    main()
