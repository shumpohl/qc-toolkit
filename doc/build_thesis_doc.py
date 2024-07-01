import functools
import os
import subprocess
import json
import sys
import pathlib
import shutil
import argparse

doc_root = pathlib.Path(__file__).parent.absolute()

original_source = doc_root / 'source'
thesis_source = doc_root / 'thesis_source'
thesis_build = doc_root / 'thesis_build'
thesis_config = doc_root / 'thesis'

parser = argparse.ArgumentParser()
parser.add_argument("targetdir", help="Directory to dump sphinx files into")
parser.add_argument("--skip-build", default=False, action='store_true')



class WarningsFormatter:
    pass


def extract_embeddable_documents(build_dir, target_dir):
    target_dir = pathlib.Path(target_dir).absolute()
    assert target_dir.exists()
    assert (target_dir / 'main.tex').exists()
    enc = 'utf-8'

    for existing_sphinx_file in target_dir.glob("*sphinx*.*"):
        existing_sphinx_file.unlink()

    for sphinx_file in build_dir.glob('*sphinx*.*'):
        if 'tableofcontents' in sphinx_file.read_text(enc):
            print('tableofcontents', sphinx_file.name)

        if 'sphinxlatexstyle' not in sphinx_file.stem:
            shutil.copy(sphinx_file, target_dir)
            txt = sphinx_file.read_text(enc)
            if 'titlesec' in txt:
                print(sphinx_file.name, 'contains titlesec')

    sphinx_sty_path = target_dir / 'sphinx.sty'
    sphinx_sty = sphinx_sty_path.read_text(enc)
    sphinx_sty = '\n'.join(
        line for line in sphinx_sty.splitlines()
        if 'sphinxlatexstyle' not in line
    )
    sphinx_sty_path.write_text(sphinx_sty)

    appendix_dir = target_dir / 'appendix' / 'qupulse_doc'

    for png in build_dir.glob('*.png'):
        shutil.copy(png, appendix_dir)

    qupulse_source = (build_dir / 'qupulse.tex').read_text(encoding=enc)
    header, rest = qupulse_source.split(r'\title', 1)
    header = '\n'.join(line for line in header.splitlines()
                       if not (line.startswith(r'\documentclass') or 'titlesec' in line or 'sphinxbackoftitlepage' in line))
    _, body = rest.split(r'\begin{document}', 1)
    body, _ = body.rsplit(r'\end{document}', 1)
    body = body.replace(r'\sphinxAtStartPar', '')

    (target_dir / 'qupulseappendix.sty').write_text(header, encoding=enc)
    (appendix_dir / 'qupulseappendix.tex').write_text(body, encoding=enc)





def extract_embeddable_documents(build_dir, target_dir):
    target_dir = pathlib.Path(target_dir).absolute()
    assert target_dir.exists()
    assert (target_dir / 'main.tex').exists()
    enc = 'utf-8'

    for existing_sphinx_file in target_dir.glob("*sphinx*.*"):
        existing_sphinx_file.unlink()

    for sphinx_file in build_dir.glob('*sphinx*.*'):
        if 'tableofcontents' in sphinx_file.read_text(enc):
            print('tableofcontents', sphinx_file.name)

        if 'sphinxlatexstyle' not in sphinx_file.stem:
            shutil.copy(sphinx_file, target_dir)
            txt = sphinx_file.read_text(enc)
            if 'titlesec' in txt:
                print(sphinx_file.name, 'contains titlesec')

    sphinx_sty_path = target_dir / 'sphinx.sty'
    sphinx_sty = sphinx_sty_path.read_text(enc)
    sphinx_sty = '\n'.join(
        line for line in sphinx_sty.splitlines()
        if 'sphinxlatexstyle' not in line
    )
    sphinx_sty_path.write_text(sphinx_sty)

    appendix_dir = target_dir / 'appendix' / 'qupulse_doc'

    for png in build_dir.glob('*.png'):
        shutil.copy(png, appendix_dir)

    qupulse_source = (build_dir / 'qupulse.tex').read_text(encoding=enc)
    header, rest = qupulse_source.split(r'\title', 1)
    header = '\n'.join(line for line in header.splitlines()
                       if not (line.startswith(r'\documentclass') or 'titlesec' in line or 'sphinxbackoftitlepage' in line))
    _, body = rest.split(r'\begin{document}', 1)
    body, _ = body.rsplit(r'\end{document}', 1)
    body = body.replace(r'\sphinxAtStartPar', '')

    (target_dir / 'qupulseappendix.sty').write_text(header, encoding=enc)
    (appendix_dir / 'qupulseappendix.tex').write_text(body, encoding=enc)


def build_latex():
    if thesis_source.exists():
        raise FileExistsError(f"Please delete {thesis_source}")

    print(f"Cloning source to {thesis_source} for non-intrusive patching")
    shutil.copytree(original_source, thesis_source, ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '_autosummary'))
    # ignore in git
    (thesis_source / '.gitignore').write_text("*")
    thesis_build.mkdir(exist_ok=True)
    (thesis_build / '.gitignore').write_text("*")

    with open(thesis_source / 'conf.py', 'a+') as fp:
        fp.write("\n\n# automatically appended")
        for key, value in settings.items():
            fp.write(f"{key} = {value!r}\n")
        fp.write("\n")

    # remove index
    index_file = thesis_source / 'index.rst'
    index_contents = index_file.read_text()
    index_contents, _ = index_contents.split("Indices and tables")
    index_file.write_text(index_contents)

    try:
        subprocess.check_call(["sphinx-build", "-blatex", "-j4", thesis_source.relative_to(doc_root), thesis_build.relative_to(doc_root)], cwd=doc_root)
    finally:
        print("Deleting patched source directory")
        shutil.rmtree(thesis_source)


def build_latex_2():
    subprocess.check_call(
        [
            "sphinx-build",
            "-blatex",
            "-j4",
            f"-c{thesis_config.relative_to(doc_root)}",
            original_source.relative_to(doc_root), thesis_build.relative_to(doc_root)],
        cwd=doc_root)


def copy_sphinx_files(target_dir):
    sphinx_files = thesis_build.glob('*sphinx*.sty')

    ignored = ('sphinxlatexstylepage', )

    for sphinx_file in sphinx_files:
        if any(x in sphinx_file.stem for x in ignored):
            continue
        else:
            shutil.copy(sphinx_file, target_dir)

    sphinx_sty_path = target_dir / 'sphinx.sty'
    sphinx_sty = sphinx_sty_path.read_text('utf-8')
    sphinx_sty = '\n'.join(
        line for line in sphinx_sty.splitlines()
        if not any(x in line for x in ignored)
    )
    sphinx_sty_path.write_text(sphinx_sty)


def extract_embeddable_documents_2(target_dir):
    target_dir = pathlib.Path(target_dir).absolute()
    assert target_dir.exists()
    assert (target_dir / 'main.tex').exists()

    appendix_dir = target_dir / 'appendix' / 'qupulse_doc'
    assert appendix_dir.exists()

    qupulse_tex = thesis_build / 'qupulse.tex'
    assert qupulse_tex.exists()

    for file in target_dir.glob('*sphinx*'):
        file.unlink()

    assets = thesis_build.glob('*.png')

    shutil.copy(qupulse_tex, appendix_dir)
    copy_sphinx_files(target_dir)

    for asset in assets:
        shutil.copy(asset, appendix_dir)



if __name__ == '__main__':
    parsed = parser.parse_args()
    if not parsed.skip_build:
        build_latex_2()

    extract_embeddable_documents_2(parsed.targetdir)




