import subprocess
import json
import sys
import pathlib
import shutil

doc_root = pathlib.Path(__file__).parent.absolute()

original_source = doc_root / 'source'
thesis_source = doc_root / 'thesis_source'
build = doc_root / 'build'

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
            'preamble': r'''
            % Disable the default title and author
            \renewcommand{\maketitle}{}
            \renewcommand{\sphinxmaketitle}{}
            \renewcommand{\sphinxbackoftitlepage}{}
            % Disable the table of contents
            \renewcommand{\tableofcontents}{}
            % Use the 'titlesec' package to remove chapter prefixes
            \usepackage{titlesec}
            \titleformat{\chapter}[display]
                {\normalfont\huge\bfseries}{}{0pt}{\Huge}
            \titleformat{name=\chapter,numberless}[display]
                {\normalfont\huge\bfseries}{}{0pt}{\Huge}
            % Customize the formatting for sections, if desired
            \titleformat{\section}
                {\normalfont\Large\bfseries}{\thesection}{1em}{}
            % Customize the formatting for subsections, if desired
            \titleformat{\subsection}
                {\normalfont\large\bfseries}{\thesubsection}{1em}{}
            % Customize the formatting for subsubsections, if desired
            \titleformat{\subsubsection}
                {\normalfont\normalsize\bfseries}{\thesubsubsection}{1em}{}
            % Customize the formatting for paragraphs, if desired
            \titleformat{\paragraph}[runin]
                {\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}
            % Customize the formatting for subparagraphs, if desired
            \titleformat{\subparagraph}[runin]
                {\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}
        ''',

    # Latex figure (float) alignment
    #'figure_align': 'htbp',
        'babel': '% use given babel',
    },
    latex_documents = [
        ('index', 'qupulse.tex', 'qupulse Documentation', 'Simon Humpohl', 'manual'),
    #    ('concepts/concepts', 'qupulse_concepts.tex', 'title_test', 'author_test', 'manual')
    ],
    latex_domain_indices = False,
)


if __name__ == '__main__':
    if thesis_source.exists():
        raise FileExistsError(f"Please delete {thesis_source}")

    print(f"Cloning source to {thesis_source} for non-intrusive patching")
    shutil.copytree(original_source, thesis_source, ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '_autosummary'))
    # ignore in git
    (thesis_source / '.gitignore').write_text("*")

    with open(thesis_source / 'conf.py', 'a+') as fp:
        fp.write("\n\n# automatically appended")
        for key, value in settings.items():
            fp.write(f"{key} = {value!r}\n")
        fp.write("\n")

    try:
        subprocess.check_call(["sphinx-build", "-blatex", "-j4", thesis_source.relative_to(doc_root), build.relative_to(doc_root)], cwd=doc_root)
    finally:
        print("Deleting patched source directory")
        shutil.rmtree(thesis_source)


