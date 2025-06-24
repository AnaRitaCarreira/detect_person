# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from typing import Any

from ultralytics.solutions.solutions import BaseSolution, SolutionAnnotator, SolutionResults
from ultralytics.utils import LOGGER
from ultralytics.utils.plotting import colors


class SecurityAlarm(BaseSolution):
    """
    A class to manage security alarm functionalities for real-time monitoring.

    This class extends the BaseSolution class and provides features to monitor objects in a frame, send email
    notifications when specific thresholds are exceeded for total detections, and annotate the output frame for
    visualization.

    Attributes:
        email_sent (bool): Flag to track if an email has already been sent for the current event.
        records (int): Threshold for the number of detected objects to trigger an alert.
        server (smtplib.SMTP): SMTP server connection for sending email alerts.
        to_email (str): Recipient's email address for alerts.
        from_email (str): Sender's email address for alerts.

    Methods:
        authenticate: Set up email server authentication for sending alerts.
        send_email: Send an email notification with details and an image attachment.
        process: Monitor the frame, process detections, and trigger alerts if thresholds are crossed.

    Examples:
        >>> security = SecurityAlarm()
        >>> security.authenticate("abc@gmail.com", "1111222233334444", "xyz@gmail.com")
        >>> frame = cv2.imread("frame.jpg")
        >>> results = security.process(frame)
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the SecurityAlarm class with parameters for real-time object monitoring.

        Args:
            **kwargs (Any): Additional keyword arguments passed to the parent class.
        """
        super().__init__(**kwargs)
        self.email_sent = False
        self.records = self.CFG["records"]
        self.server = None
        self.to_email = ""
        self.from_email = ""
        self.save_folder = "./detected_person"

    def set_save_folder(self, folder_path: str) -> None:
        """
        Define o diretório onde as imagens detetadas serão guardadas.
        """
        self.save_folder = folder_path

    def authenticate(self, from_email: str, password: str, to_email: str) -> None:
        """
        Authenticate the email server for sending alert notifications.

        Args:
            from_email (str): Sender's email address.
            password (str): Password for the sender's email account.
            to_email (str): Recipient's email address.

        This method initializes a secure connection with the SMTP server and logs in using the provided credentials.

        Examples:
            >>> alarm = SecurityAlarm()
            >>> alarm.authenticate("sender@example.com", "password123", "recipient@example.com")
        """
        import smtplib

        self.server = smtplib.SMTP("smtp.gmail.com: 587")
        self.server.starttls()
        self.server.login(from_email, password)
        self.to_email = to_email
        self.from_email = from_email

    def send_email(self, im0, records: int = 5) -> None:
        """
        Send an email notification with an image attachment indicating the number of objects detected.

        Args:
            im0 (numpy.ndarray): The input image or frame to be attached to the email.
            records (int, optional): The number of detected objects to be included in the email message.

        This method encodes the input image, composes the email message with details about the detection, and sends it
        to the specified recipient.

        Examples:
            >>> alarm = SecurityAlarm()
            >>> frame = cv2.imread("path/to/image.jpg")
            >>> alarm.send_email(frame, records=10)
        """
        from email.mime.image import MIMEImage
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        import cv2

        img_bytes = cv2.imencode(".jpg", im0)[1].tobytes()  # Encode the image as JPEG

        # Create the email
        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = self.to_email
        message["Subject"] = "Security Alert"

        # Add the text message body
        message_body = f"Ultralytics ALERT!!! {records} objects have been detected!!"
        message.attach(MIMEText(message_body))

        # Attach the image
        image_attachment = MIMEImage(img_bytes, name="ultralytics.jpg")
        message.attach(image_attachment)

        # Send the email
        try:
            self.server.send_message(message)
            LOGGER.info("Email sent successfully!")
        except Exception as e:
            LOGGER.error(f"Failed to send email: {e}")

    def process(self, im0) -> SolutionResults:
        """
        Monitor the frame, process object detections, and trigger alerts if a person (class 0) is detected.
        """
        import os
        from datetime import datetime
        import cv2
        from pygame import mixer
        import time

        self.extract_tracks(im0)  # Extract tracks
        annotator = SolutionAnnotator(im0, line_width=self.line_width)  # Initialize annotator

        person_detected = False

        for box, cls in zip(self.boxes, self.clss):
            annotator.box_label(box, label=self.names[cls], color=colors(cls, True))

            if cls == 0:  # Class 0 = 'person'
                person_detected = True

                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print("PERSON detected")
                print("Current Time =", current_time)

                folder = "./detected_person/"
                os.makedirs(folder, exist_ok=True)

                image_detection = im0.copy()
                current_datetime_file = now.strftime("%Y_%m_%d_%H_%M_%S_%f")
                current_datetime_text = now.strftime("%Y/%m/%d - %H:%M:%S:%f")

                h, w, _ = image_detection.shape
                cv2.putText(image_detection, current_datetime_text, (15, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

                filename = folder + current_datetime_file + '.png'
                cv2.imwrite(filename, image_detection)

                # Reproduzir som de alarme
                mixer.init()
                mixer.music.load('./sounds/alarm.mp3')
                mixer.music.play()

                # Enviar email se ainda não foi enviado
                if not self.email_sent:
                    self.send_email(image_detection, records=1)
                    self.email_sent = True

                time.sleep(10)  # Aguarda para não detetar continuamente a mesma pessoa

        plot_im = annotator.result()
        self.display_output(plot_im)

        return SolutionResults(plot_im=plot_im, total_tracks=len(self.track_ids), email_sent=self.email_sent)