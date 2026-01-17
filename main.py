from src.presentation.app import StudentManagerApp
import sys

def main() -> None:
    """
    Composition Root for the Student Manager application.

    This entry point initializes the presentation layer which, in turn,
    wires up the infrastructure and domain use cases.
    """

    if "--tui" in sys.argv:
        app = StudentManagerApp()
        app.run()
 
if __name__ == "__main__":
    main()
