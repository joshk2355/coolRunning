import time
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('edit_spredsheets.json',scope)

client = gspread.authorize(creds)

sheet = client.open('Cross-CountryTimes').sheet1

class StopwatchApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
        self.elapsed_time = 0.0
        self.is_running = False
        self.time_label = Label(text="Time: 00:00.0", font_size=40)
        self.update_event = None
        self.buttonArray = []
        self.main_layout = BoxLayout(orientation='horizontal')
        self.right_layout = BoxLayout(orientation='vertical')




    def build(self):

        main_layout = self.main_layout
        # Left vertical layout for the stopwatch display and controls
        left_layout = BoxLayout(orientation='vertical')
        left_layout.add_widget(self.time_label)

        # Start/Stop button
        self.start_stop_button = Button(text="Start", font_size=32, size_hint=(1, 0.2))
        self.start_stop_button.bind(on_press=self.start_stop_watch)
        left_layout.add_widget(self.start_stop_button)

        # Reset button
        reset_button = Button(text="Reset", font_size=32, size_hint=(1, 0.2))
        reset_button.bind(on_press=self.reset_watch)
        left_layout.add_widget(reset_button)

        # Right vertical layout for the "Time" buttons with names
        right_layout = self.right_layout

        # Dropdown Button
        dropdown = DropDown()

        print(sheet.get_all_records())
        runners = []
        for item in sheet.get_all_records():
            if item["Runner"]:
                runners.append(item['Runner'])
        print(runners)

        for name in runners:
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.
            btn = Button(text=name, size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=self.add_button)#dropdown.select(btn.text))
            dropdown.add_widget(btn)



        # create a big main button
        mainbutton = Button(text='Add Runners', font_size=32, size_hint=(1, 0.2))

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        mainbutton.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        left_layout.add_widget(mainbutton)

        # Add the left and right layouts to the main layout
        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        return main_layout





    def update_time(self, dt):
        """Update the displayed time every frame."""
        if self.is_running:
            # Calculate total elapsed time
            current_time = time.time()
            total_time = current_time - self.start_time + self.elapsed_time
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            milliseconds = int((total_time % 1) * 1000)  # Extract milliseconds from the fractional part
            self.time_label.text = f"Time: {minutes:02}:{seconds:02}.{milliseconds:03}"

    def start_stop_watch(self, instance):
        """Start or stop the stopwatch."""
        if not self.is_running:
            # Start the stopwatch
            self.start_time = time.time()
            self.is_running = True
            instance.text = "Stop"

            # Schedule updates every 0.1 seconds
            if not self.update_event:
                self.update_event = Clock.schedule_interval(self.update_time, 0.1)
        else:
            # Stop the stopwatch and accumulate elapsed time
            self.elapsed_time += time.time() - self.start_time
            self.is_running = False
            instance.text = "Start"

            # Stop updating the time
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None

    def reset_watch(self, instance):
        """Reset the stopwatch."""
        self.elapsed_time = 0.0
        self.start_time = None
        self.is_running = False
        self.time_label.text = "Time: 00:00.0"
        self.start_stop_button.text = "Start"

        # Cancel any scheduled updates
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

        self.right_layout.clear_widgets()


    def save_current_time(self, instance):
        """Update the button text with the name and current time."""
        name = instance.text
        runners = []
        for item in sheet.get_all_records():
            if item["Runner"]:
                runners.append(item['Runner'])

        # Get the current stopwatch time
        current_time = self.time_label.text

        index = runners.index(name) + 2

        # Set button text to "Name: Time"
        instance.text = f"{instance.text.split(':')[0]}: {current_time}"
        sheet.delete_rows(index, index)
        # Send the Time to the Sheet
        sheet.append_row([instance.text.split(':')[0], current_time])

        # Set button to disabled
        instance.disabled = True



    def add_button(self, instance):
        button = Button(text=instance.text,  font_size=32, size_hint=(1, 0.2))
        self.buttonArray.append(button)
        print(self.buttonArray)
        button.bind(on_press=self.save_current_time)
        self.right_layout.add_widget(button)








if __name__ == '__main__':
    StopwatchApp().run()
