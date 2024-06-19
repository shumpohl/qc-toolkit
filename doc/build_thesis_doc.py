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

REDEFINE_RM = r'''
\renewcommand{\rmdefault}{\rmfamily}
\renewcommand{\sfdefault}{\sffamily}
\renewcommand{\ttdefault}{\ttfamily}
'''

KOMA_SECTION_FORMAT = r'''
% Use KOMA-Script's section formatting
\RedeclareSectionCommand[
beforeskip=-3.5ex plus -1ex minus -.2ex,
afterskip=2.3ex plus .2ex
]{section}
\RedeclareSectionCommand[
beforeskip=-3.25ex plus -1ex minus -.2ex,
afterskip=1.5ex plus .2ex
]{subsection}
\RedeclareSectionCommand[
beforeskip=-3.25ex plus -1ex minus -.2ex,
afterskip=1.5ex plus .2ex
]{subsubsection}
\RedeclareSectionCommand[
beforeskip=-3.25ex plus -1ex minus -.2ex,
afterskip=1.5ex plus .2ex
]{paragraph}
\RedeclareSectionCommand[
beforeskip=-3.25ex plus -1ex minus -.2ex,
afterskip=1.5ex plus .2ex
]{subparagraph}'''

TEXT_COMP = r"""
\usepackage{textcomp}
"""

settings = dict(
    latex_engine = 'lualatex',
    latex_toplevel_sectioning = 'section',
    latex_elements = {
        # The paper size ('letterpaper' or 'a4paper').
        'papersize': 'a4paper',

        # The font size ('10pt', '11pt' or '12pt').
        'pointsize': '12pt',

        # Additional stuff for the LaTeX preamble.
            'extraclassoptions': 'openany',  # Optional: Remove blank pages between chapters
            'preamble': TEXT_COMP,

    # Latex figure (float) alignment
    #'figure_align': 'htbp',
        'babel': '',
        'fontenc': '',
        'inputenc': '',
        'utf8extra': '',
        'cmappkg': '',
        'geometry': r'\usepackage{geometry}',
        'hyperref': r'\usepackage{hyperref}',
    },
    latex_documents = [
    #    ('index', 'qupulse.tex', 'qupulse Documentation', 'Simon Humpohl', 'manual'),
        ('concepts/concepts', 'qupulse_concepts.tex', 'title_test', 'author_test', 'manual'),
    #    ('learners_guide', 'qupulse_learners_guide.tex', 'title_test', 'author_test', 'manual'),
    #    ('_autosummary/qupulse', 'qupulse_reference.tex', 'title_test', 'author_test', 'manual')
    ],
    latex_domain_indices = False,
)

parser = argparse.ArgumentParser()
parser.add_argument("targetdir", help="Directory to dump sphinx files into")
parser.add_argument("--skip-build", default=False, action='store_true')

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


if __name__ == '__main__':
    parsed = parser.parse_args()

    if not parsed.skip_build:
        build_latex()

    extract_embeddable_documents(thesis_build, parsed.targetdir)




