from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from plyer import gps
from android.permissions import request_permissions, Permission

class SMSLocationApp(App):
    def build(self):
        # Yêu cầu quyền Runtime từ người dùng khi mở ứng dụng
        request_permissions([
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.SEND_SMS
        ])

        self.target_phone = ""
        self.current_lat = None
        self.current_lon = None
        self.is_running = False

        # Giao diện người dùng (UI)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text="TỰ ĐỘNG GỬI TỌA ĐỘ QUA SMS", font_size='18sp'))

        self.phone_input = TextInput(hint_text="Nhập số điện thoại nhận (vd: 0987654321)", multiline=False)
        layout.add_widget(self.phone_input)

        self.interval_input = TextInput(hint_text="Khoảng thời gian gửi (phút)", text="5", multiline=False)
        layout.add_widget(self.interval_input)

        self.status_label = Label(text="Trạng thái: Đang dừng")
        layout.add_widget(self.status_label)

        self.toggle_btn = Button(text="Bắt đầu tự động gửi", on_press=self.toggle_sending)
        layout.add_widget(self.toggle_btn)

        # Cấu hình dịch vụ GPS
        try:
            gps.configure(on_location=self.on_location_update)
        except Exception as e:
            self.status_label.text = f"Lỗi khởi tạo GPS: {str(e)}"

        return layout

    def on_location_update(self, **kwargs):
        self.current_lat = kwargs.get('lat')
        self.current_lon = kwargs.get('lon')

    def send_sms_native(self, phone, message):
        """Gọi API gốc SmsManager của Android qua Pyjnius"""
        try:
            from jnius import autoclass
            SmsManager = autoclass('android.telephony.SmsManager')
            sms = SmsManager.getDefault()
            sms.sendTextMessage(str(phone), None, str(message), None, None)
            return True
        except Exception as e:
            print(f"SMS Error: {e}")
            return False

    def process_and_send(self, dt):
        if not self.target_phone:
            return

        if self.current_lat is not None and self.current_lon is not None:
            maps_link = f"https://maps.google.com/?q={self.current_lat},{self.current_lon}"
            msg = f"Vi tri hien tai: {maps_link}"
            
            success = self.send_sms_native(self.target_phone, msg)
            if success:
                self.status_label.text = "Đã gửi tọa độ thành công!"
            else:
                self.status_label.text = "Gửi SMS thất bại."
        else:
            self.status_label.text = "Đang chờ dữ liệu GPS..."

    def toggle_sending(self, instance):
        if not self.is_running:
            phone = self.phone_input.text.strip()
            if not phone:
                self.status_label.text = "Vui lòng nhập số điện thoại!"
                return

            try:
                interval_minutes = float(self.interval_input.text.strip())
                interval_seconds = max(interval_minutes * 60, 10) # Tối thiểu 10 giây
            except ValueError:
                self.status_label.text = "Thời gian không hợp lệ!"
                return

            self.target_phone = phone
            self.is_running = True
            self.toggle_btn.text = "Dừng gửi"
            self.status_label.text = "Đang chạy..."

            try:
                gps.start(1000, 0)
            except Exception as e:
                print(f"GPS Start error: {e}")

            Clock.schedule_interval(self.process_and_send, interval_seconds)
        else:
            self.is_running = False
            self.toggle_btn.text = "Bắt đầu tự động gửi"
            self.status_label.text = "Trạng thái: Đang dừng"
            Clock.unschedule(self.process_and_send)
            try:
                gps.stop()
            except Exception:
                pass

if __name__ == '__main__':
    SMSLocationApp().run()