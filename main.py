import json
import os


class ProgrammerDictionary:
    def __init__(self, locale='en-US'):
        self.locale = locale
        self.dictionary_file = f'definitions/{locale}.json'
        data = self._load_definitions()
        self.menu = data.get('menu', {})
        self.definitions = data.get('terms', {})
        self.categories = data.get('categories', [])
        self.related_terms = self._build_related_terms()

    def _load_definitions(self):
        """Load definitions from JSON file."""
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"menu": {}, "terms": {}, "categories": []}

    def _build_related_terms(self):
        """Build a mapping of search queries to their primary terms."""
        related = {}
        for term, data in self.definitions.items():
            # Only add search queries if they exist
            if 'search_queries' in data:
                for query in data['search_queries']:
                    related[query.upper()] = term
            # Add the main term as a search query too
            related[term] = term
        return related

    def lookup_term(self, term):
        """Look up a programming term."""
        term = term.upper()
        # Check if it's a related term
        if term in self.related_terms:
            primary_term = self.related_terms[term]
            return self.definitions[primary_term]
        return None

    def add_term(self, term, definition, categories, examples=None,
                 search_queries=None):
        """Add a new term to the dictionary."""
        term = term.upper()
        self.definitions[term] = {
            "definition": definition,
            "categories": categories,  # Now accepts an array of categories
            "examples": examples or [],
            "search_queries": search_queries or []
        }
        self.related_terms = self._build_related_terms()
        self._save_definitions()

    def lookup_by_category(self, category):
        """Look up all terms in a specific category."""
        return {term: data for term, data in self.definitions.items()
                if category in data['categories']}

    def _save_definitions(self):
        """Save definitions back to JSON file."""
        data = {
            "menu": self.menu,
            "categories": self.categories,
            "terms": self.definitions
        }
        with open(self.dictionary_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


def main():
    print("Locale:")
    print("1. English (United States) [en-US]")

    while True:
        locale_choice = input("\nSelect locale (default: en-US): ").strip()
        if locale_choice == "" or locale_choice == "1":
            locale = "en-US"
            break
        else:
            print("Invalid locale! Please try again.")

    dictionary = ProgrammerDictionary(locale)
    menu = dictionary.menu  # Get menu translations for selected locale

    print(f"\n{menu['welcome']}")  # Now show welcome message after locale selection

    while True:
        print(f"\n{menu['title']}")
        print(f"1. {menu['options']['lookup']}")
        print(f"2. {menu['options']['add']}")
        print(f"3. {menu['options']['category_lookup']}")
        print(f"4. {menu['options']['exit']}")

        choice = input(f"\n{menu['prompts']['choice']}")

        if choice == '1':
            term = input(menu['prompts']['term_lookup'])
            result = dictionary.lookup_term(term)
            if result:
                print(
                    f"\n{menu['labels']['definition']}: {result['definition']}")
                print(f"{menu['labels']['category']}: {result['category']}")
                if result['examples']:
                    print(
                        f"{menu['labels']['examples']}: {', '.join(result['examples'])}")
                print("\n")
            else:
                print(menu['messages']['term_not_found'])

        elif choice == '2':
            term = input(menu['prompts']['term_add'])
            definition = input(menu['prompts']['definition'])

            # Show available categories
            print("\nAvailable categories:")
            for i, category in enumerate(dictionary.categories, 1):
                print(f"{i}. {category}")

            categories = []
            while True:
                category_input = input(menu['prompts']['categories'])
                if not category_input:
                    break

                for cat_choice in category_input.split(','):
                    cat_choice = cat_choice.strip()
                    try:
                        category_index = int(cat_choice) - 1
                        if 0 <= category_index < len(dictionary.categories):
                            categories.append(dictionary.categories[category_index])
                        else:
                            print(f"Invalid category number: {cat_choice}")
                    except ValueError:
                        if cat_choice in dictionary.categories:
                            categories.append(cat_choice)
                        else:
                            print(f"Invalid category: {cat_choice}")

                if categories:
                    break
                print("Please enter at least one valid category!")

            examples = input(menu['prompts']['examples'])
            search_queries = input(menu['prompts']['search_queries'])

            examples = [e.strip() for e in examples.split(',')] if examples else []
            search_queries = [q.strip()
                              for q in search_queries.split(',')] if search_queries else [
            ]

            dictionary.add_term(term, definition, categories, examples, search_queries)
            print(menu['messages']['term_added'])

        elif choice == '3':
            # Show available categories
            print("\nAvailable categories:")
            for i, category in enumerate(dictionary.categories, 1):
                print(f"{i}. {category}")

            category_choice = input(menu['prompts']['category_lookup'])
            try:
                category_index = int(category_choice) - 1
                if 0 <= category_index < len(dictionary.categories):
                    category = dictionary.categories[category_index]
                else:
                    print("Invalid category number!")
                    continue
            except ValueError:
                if category_choice not in dictionary.categories:
                    print("Invalid category!")
                    continue
                category = category_choice

            results = dictionary.lookup_by_category(category)
            if results:
                print(f"\nTerms in category '{category}':")
                for term, data in results.items():
                    print(f"\n{term}:")
                    print(f"  {menu['labels']['definition']}: {data['definition']}")
                    if data['examples']:
                        print(
                            f"  {menu['labels']['examples']}: {', '.join(data['examples'])}")
                print()
            else:
                print(menu['messages']['no_terms_in_category'])

        elif choice == '4':
            print(menu['messages']['goodbye'])
            break

        else:
            print(menu['messages']['invalid_choice'])


if __name__ == "__main__":
    main()
