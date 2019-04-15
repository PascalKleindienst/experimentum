from __future__ import print_function
from experimentum.Commands import command
from termcolor import colored


@command(
    'Displays between one and ten lorem ipsum sentences.',
    arguments={
        'sentences': {
            'type': int, 'action': 'store', 'help': 'Number of sentences toe display.'
        }
    },
    help='Display lorem ipsum text'
)
def lorem(app, args):
    """Display lorem ipsum text."""
    content = [
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
        "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
        "At vero eos et accusam et justo duo dolores et ea rebum.",
        "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "\n\nLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
        "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
        "At vero eos et accusam et justo duo dolores et ea rebum.",
        "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
        "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
        "At vero eos et accusam et justo duo dolores et ea rebum.",
        "\n\nStet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor"
        "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua."
    ]

    # Clamp sentences to content range
    sentences = max(0, min(args.sentences, len(content)-1))

    print(colored(' '.join(content[:sentences]), 'yellow'))
