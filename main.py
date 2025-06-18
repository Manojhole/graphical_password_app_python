from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import validate_user, connect_db, register_user, login_user, get_password_by_mobile
from password_logic import save_graphical_password
import os
import sqlite3  # Needed for ForgotGraphicalScreen

# Load all .kv screens
for kv_file in ["login.kv", "register.kv", "forgot.kv", "dashboard.kv",
                "select_app.kv", "choose_category.kv", "grid_password.kv"]:
    Builder.load_file(f"screens/{kv_file}")


# ----- SCREEN CLASSES -----

class LoginScreen(Screen):
    def login_user(self):
        mobile = self.ids.mobile_input.text
        password = self.ids.password_input.text
        if validate_user(mobile, password):
            self.manager.get_screen('dashboard').ids.welcome_label.text = f"welcome {mobile}"
            self.manager.current = 'dashboard'
        else:
            Popup(title='Login Failed',
                  content=Label(text='Invalid mobile number or password.'),
                  size_hint=(0.8, 0.3)).open()


class RegisterScreen(Screen):
    def register(self):
        name = self.ids.name.text
        mobile = self.ids.mobile.text
        password = self.ids.password.text
        hint = self.ids.hint.text
        if register_user(name, mobile, password, hint):
            self.manager.current = 'login'
        else:
            print("Mobile number already registered")


class ForgotScreen(Screen):
    def retrieve(self):
        mobile = self.ids.mobile.text
        password = get_password_by_mobile(mobile)
        if password:
            self.ids.result.text = f"Your password is: {password}"
        else:
            self.ids.result.text = "Mobile not found"


class DashboardScreen(Screen):
    user_mobile = ''

    def go_to_app_locker(self):
        self.manager.get_screen('select_app').user_mobile = self.user_mobile
        self.manager.current = 'select_app'


class SelectAppScreen(Screen):
    user_mobile = ''

    def select_app(self, app_name):
        choose_cat_screen = self.manager.get_screen('choose_category')
        choose_cat_screen.app_name = app_name
        choose_cat_screen.user_mobile = self.user_mobile
        self.manager.current = 'choose_category'


class ChooseCategoryScreen(Screen):
    app_name = ''
    user_mobile = ''

    def set_category(self, category):
        screen = self.manager.get_screen('grid_password')
        screen.load_images(category, self.app_name, self.user_mobile)
        self.manager.current = 'grid_password'


class ImageButton(ButtonBehavior, Image):
    pass


class GridPasswordScreen(Screen):
    selected_images = []
    category = ''
    app_name = ''
    user_mobile = ''

    def load_images(self, category, app_name, user_mobile):
        self.ids.image_grid.clear_widgets()
        self.selected_images = []
        self.category = category
        self.app_name = app_name
        self.user_mobile = user_mobile

        folder = f"assets/{category}"

        print("Loading images from:", folder)

        if not os.path.exists(folder):
            print("Folder not found:", folder)
            return

        for img in os.listdir(folder):
            img_path = os.path.join(folder, img)
            if img.endswith(".png"):
                print("Adding image:", img_path)
                btn = ImageButton(source=img_path, size_hint_y=None, height=150)
                btn.image_id = img
                btn.bind(on_press=self.select_image)
                self.ids.image_grid.add_widget(btn)

    def select_image(self, btn):
        if btn.image_id not in self.selected_images:
            self.selected_images.append(btn.image_id)
            btn.opacity = 0.5
        else:
            self.selected_images.remove(btn.image_id)
            btn.opacity = 1.0

    def confirm_password(self):
        if len(self.selected_images) < 4:
            print("Select at least 4 images!")
            return

        hint = self.ids.hint_input.text.strip()
        if not hint:
            print("Please provide a hint.")
            return

        save_graphical_password(self.user_mobile, self.app_name, self.selected_images, hint)
        print(f"Graphical password set for {self.app_name}!")
        self.manager.current = 'dashboard'


class ForgotGraphicalScreen(Screen):
    def retrieve_hint(self):
        mobile = self.ids.mobile.text
        app_name = self.ids.app_spinner.text
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT hint FROM graphical_passwords WHERE mobile=? AND app_name=?", (mobile, app_name))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.ids.hint_label.text = f"Hint: {result[0]}"
        else:
            self.ids.hint_label.text = "No password set or invalid data."


# ----- APP CLASS -----

class MainApp(App):
    def build(self):
        connect_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ForgotScreen(name='forgot'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(SelectAppScreen(name='select_app'))
        sm.add_widget(ChooseCategoryScreen(name='choose_category'))
        sm.add_widget(GridPasswordScreen(name='grid_password'))
        sm.add_widget(ForgotGraphicalScreen(name='forgot_graphical'))
        return sm


if __name__ == '__main__':
    MainApp().run()
