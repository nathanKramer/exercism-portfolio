#! /usr/local/bin/python3
import os
import sys

EXERCISM_DIR = os.getenv('EXERCISM_DIR')

LANGUAGE_METADATA = {
    'c': {
        'source': 'src',
        'extension': 'c'
    },
    'clojure': {
        'source': 'src',
        'extension': 'clj'
    },
    'elixir': {
        'source': 'lib',
        'extension': 'ex'
    },
    'elm': {
        'source': 'src',
        'extension': 'elm'
    },
    'go': {
        'source': '',
        'extension': 'go'
    },
    'haskell': {
        'source': 'src',
        'extension': 'hs',
        'filename': {
            'rna-transcription': 'DNA',
            'leap': 'LeapYear'
        }
    },
    'nim': {
        'source': '',
        'extension': 'nim'
    },
    'ocaml': {
        'source': '',
        'extension': 'ml'
    },
    'prolog': {
        'source': '',
        'extension': 'pl'
    },
    'python': {
        'source': '',
        'extension': 'py'
    },
    'racket': {
        'source': '',
        'extension': 'rkt'
    },
    'rust': {
        'source': 'src',
        'extension': 'rs',
        'filename': 'lib'
    }
}


def is_relevant(subdir):
    return not subdir.startswith('.')


def subdirectories(path):
    return list(
        filter(
            lambda p: is_relevant(p) and os.path.isdir('/'.join([path, p])),
            os.listdir(path)
        )
    )


def subfiles(path):
    return list(
        filter(
            lambda p: is_relevant(p) and os.path.isfile('/'.join([path, p])),
            os.listdir(path)
        )
    )


def lookupLanguageMetadata(language):
    try:
        return LANGUAGE_METADATA[language]
    except KeyError as _keyErr:
        print(f'Unsupported language: {language}', file=sys.stderr)


def resolveSolution(rootDir, problem, metadata):
    def solution_file_name(problem):
        return f'{rootDir}/{problem}.{metadata["extension"]}'
    metadataLookup = metadata.get('filename')
    if metadataLookup is not None:
        if type(metadataLookup) is dict:
            metadataLookup = metadataLookup.get(problem)

    words = problem.split('-')
    attempts = [
        problem,  # naive
        '_'.join(words),  # snake
        ''.join([word.capitalize() for word in words]),  # camel
        '-'.join(words), # kebab
        metadataLookup  # hardcoded
    ]
    for attempt in attempts:
        file = attempt and solution_file_name(attempt)
        if file is None or not os.path.isfile(file):
            continue
        return file
    return None


def solution(language, problem):
    problem_dir = f'{EXERCISM_DIR}/{language}/{problem}'
    metadata = lookupLanguageMetadata(language)
    if not metadata:
        return None
    if metadata['source']:
        problem_dir = f'{problem_dir}/{metadata["source"]}'

    solution_file = resolveSolution(problem_dir, problem, metadata)
    if solution_file is None:
        print(f'Could not resolve solution for {language}/{problem} #FIXME')
        return None
    with open(solution_file, 'r') as f:
        return f.read()


def titlize(kebab):
    return ' '.join([word.capitalize() for word in kebab.split('-')])


def renderPage(rootDir, title, summary, items, markup):
    return f"""
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/assets/prism.css" />
            <link rel="stylesheet" href="/assets/style.css" />
        </head>
        <body>
            <div class="side-bar">
            <h2>{title}</h2>
            <p>{summary}</p>
            <ul>
              <li><a href="/index.html">Home</a></li>
            </ul>
            <ul>{"".join([ f'<li><a href="#{item}">{titlize(item)}</a></li>' for item in items])}</ul>
            </div>
            <div class="main">
            {markup}
            </div>
        </body>
        <script src="/assets/prism.js"></script>
        </html>
        """


def languagePage(rootDir, language, problems):
    solutions = []

    for problem in problems:
        solution_code = solution(language, problem)
        if solution_code is None:
            continue
        solution_markup = f"""
            <h3><a name="{problem}">{titlize(problem)}</a></h3>
            <a href="/problems/{problem}.html">Other "{titlize(problem)}" solutions.</a>
            <pre><code class="language-{language}">{solution_code}</code></pre>
        """
        solutions.append(solution_markup)
    solutions_markup = "\n".join(solutions)
    problems = [problem for problem in problems if solution(language, problem)]
    return renderPage(
        rootDir,
        titlize(language),
        f'Problems solved in {language}.',
        problems,
        solutions_markup
    )


def problemPage(rootDir, problem, languages):
    solutions = []

    for language in languages:
        solution_code = solution(language, problem)
        if solution_code is None:
            continue
        solution_markup = f"""
            <h3><a name="{language}">{titlize(language)}</a></h3>
            <a href="/languages/{language}.html">Other {titlize(language)} solutions.</a>
            <pre><code class="language-{language}">{solution_code}</code></pre>
        """
        solutions.append(solution_markup)
    solutions_markup = "\n".join(solutions)
    languages = [
        language for language in languages if solution(language, problem)]
    return renderPage(
        rootDir,
        titlize(problem),
        f'Solutions to {problem} in various languages.',
        languages,
        solutions_markup
    )


def renderIndexPage(root, portfolio):
    return f"""
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/assets/prism.css" />
            <link rel="stylesheet" href="/assets/style.css" />
        </head>
        <body>
            <article>
                <h2>Exercism Portfolio</h2>
                <h3>About</h3>
                <p>The code here is pulled straight from my <a href="https://exercism.io/profiles/nathanKramer">exercism.io profile</a>.</p>
                <p>I use exercism.io for learning purposes, so while all code here is authored by me, I do often learn from the solutions of others.</p>
                <h3>Languages</h3>
                <ul>{"".join([ f'<li><a href="/languages/{language}.html">{titlize(language)}</a></li>' for language in portfolio['languages'].keys()])}</ul>
                <h3>Problems</h3>
                <ul>{"".join([ f'<li><a href="/problems/{problem}.html">{titlize(problem)}</a></li>' for problem in portfolio['problems'].keys()])}</ul>
            </article>
        </body>
        </html>
        """


def writePortfolioToFile(root, portfolio):
    for key in portfolio.keys():
        workingDir = f'{root}/{key}'
        child = portfolio[key]
        if child is None:
            continue
        if type(child) is dict:
            writePortfolioToFile(workingDir, child)
        else:
            with open(f'{workingDir}.html', 'w+') as solutionPage:
                print(f'Writing: {workingDir}.html')
                solutionPage.write(child)


def main():
    if EXERCISM_DIR is None:
        raise Exception("EXERCISM_DIR is required")

    languages = subdirectories(EXERCISM_DIR)
    problems_by_lang = {}
    langs_by_problem = {}

    for language in languages:
        problems = subdirectories(f'{EXERCISM_DIR}/{language}')
        problems.sort()
        problems_by_lang[language] = problems
        for problem in problems:
            language_list = langs_by_problem.get(problem, [])
            language_list.append(language)
            langs_by_problem[problem] = language_list

    portfolio = {
        'languages': {lang: languagePage(os.getcwd(), lang, problems) for lang, problems in iter(problems_by_lang.items())},
        'problems': {problem: problemPage(os.getcwd(), problem, languages) for problem, languages in iter(langs_by_problem.items())}
    }

    os.makedirs("pages", exist_ok=True)
    os.makedirs("pages/problems", exist_ok=True)
    os.makedirs("pages/languages", exist_ok=True)

    with open(f'pages/exercism.html', 'w+') as indexPage:
        print(f'Writing: exercism.html')
        indexPage.write(renderIndexPage(os.getcwd(), portfolio))

    writePortfolioToFile(
        f"{os.getcwd()}/pages",
        portfolio
    )


if __name__ == '__main__':
    main()
