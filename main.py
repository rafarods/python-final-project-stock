import views.login_window as login_window
import views.main_window as main_window

def main() -> None:
    """
    Control de ventanas de inicio de sesión
    """
    while True:
        user: dict | None = login_window.show()
        if user is None:
            break
        logout: bool = main_window.show(user)
        if not logout:
            break

if __name__ == "__main__":
    main()