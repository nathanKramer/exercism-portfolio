#! /usr/local/bin/python3
import os

EXERCISM_DIR = '/Users/nathankramer/Projects/exercism'

LANGUAGE_METADATA={
    'elm': {
        'source': 'src',
        'extension': 'elm'
    },
    'haskell': {
        'source': 'src',
        'extension': 'hs'
    },
    'python': {
        'source': '',
        'extension': 'py'
    }
}

def subdirectories(path):
    return os.listdir(path)

def subfiles(path):
    return filter(
        os.path.isfile,
        os.listdir(path)
    )

def solution(language, problem):
    problem_dir = f'{EXERCISM_DIR}/{language}/{problem}'
    metadata = LANGUAGE_METADATA[language]
    if metadata['source']:
        problem_dir = f'{problem_dir}/{metadata["source"]}'
    solution_file = f'{problem_dir}/{problem}.{metadata["extension"]}'
    if not os.path.isfile(solution_file):
        print(f'Could not resolve solution for {problem} #FIXME')
        return None

    with open(solution_file, 'r') as f:
        return f.readlines()


def languagePage(language, problems):
    solutions = []
    for problem in problems:
        solution_code = solution(language, problem)
        if solution_code is None:
            continue
        solution_markup = f"""
        <pre>
          <code class="lang-{language}">
            {solution_code}
          <\/code>
        </pre>
        """
        solutions.append(solution_markup)
    solutions_markup = "\n".join(solutions)
    return f"""
    <html>
      <body>
        {solutions_markup}
      </body>
    </html>
    """

def main():
    languages = subdirectories(EXERCISM_DIR)
    problems_by_lang = {}
    langs_by_problem = {}

    for language in languages:
        problems = os.listdir(f'{EXERCISM_DIR}/{language}')
        problems_by_lang[language] = problems
        for problem in problems:
            language_list = langs_by_problem.get(problem, [])
            language_list.append(language)
            langs_by_problem[problem] = language_list
    print(problems_by_lang)
    print()
    print(langs_by_problem)
    pages = [ print(languagePage(language, problems_by_lang[language])) for language in problems_by_lang.keys() ]

if __name__ == '__main__':
    main()
