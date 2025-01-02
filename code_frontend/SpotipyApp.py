# import libraries
from code_backend.music_classes import Album, Artist, Device, Genre, Player, Playlist, Track, TrackAnalysis, User
from code_backend.secondary_methods import *
from shared_config import *

button_image_size = 20
window_size = '800x400'
app_icon = image_from_file(file_path='Icons/Spotipy_Logo.png')

# Player Icons:
shuffle_off_path = 'Icons/shuffle_off.png'
shuffle_on_path = 'Icons/shuffle.png'

prev_track_path = 'Icons/prev.png'
play_path = 'Icons/play.png'
pause_path = 'Icons/pause.png'
next_track_path = 'Icons/next.png'

repeat_context_path = 'Icons/repeat_context.png'
repeat_track_path = 'Icons/repeat_track.png'
repeat_off_path = 'Icons/repeat_off.png'

# Track
add_queue = 'Icons/queue.png'


def get_tk_image_icons(image_path: str) -> ImageTk:
    if not os.path.exists(image_path):
        raise FileNotFoundError

    image = tk_image_from_file(file_path=image_path)
    if image is None:
        raise Exception("Image could not be loaded")

    return get_tk_image(
        image=image,
        image_size=[button_image_size, button_image_size]
    )


class SpotifyAppWindow:
    def __init__(self) -> None:
        master = Tk()

        image: PhotoImage = ImageTk.PhotoImage(app_icon)
        master.wm_iconphoto(False, image)

        master.title('Spotipy Client')
        master.geometry(window_size)
        master.resizable(False, False)

        self.sp = try_spotify_connection()
        self.player = spotify_App.player
        self.repeat_state = self.player.repeat_state

        self.instance_option_buttons_needed = BooleanVar(value=False)
        self.search_buttons_needed = BooleanVar(value=False)
        self.yes_button_pressed = IntVar(value=0)
        self.current_volume = IntVar(value=self.player.device.volume_percent)  # 0 <= vol:int <= 100
        self.progress_sec = IntVar(value=self.player.progress)  # int in seconds

        self.mainframe = Frame(master)
        self.mainframe.config(bg=backcolor)

        self.bold_font = Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = Font(family="Helvetica", size=12)
        self.input_font = Font(family="Helvetica", size=19)

        self.progress_bar_style = ttk.Style()
        self.progress_bar_style.theme_use("clam")
        self.progress_bar_style.configure(
            style="design.Horizontal.TProgressbar",
            background=backcolor,
            troughcolor=textcolor,
            bordercolor=backcolor
        )

        global image_shuffle_off
        global image_shuffle_on
        global image_prev_track
        global image_play
        global image_pause
        global image_next_track
        global image_repeat_context
        global image_repeat_track
        global image_repeat_off
        global image_add_queue

        image_shuffle_off = tk_image_from_file(file_path=shuffle_off_path)
        image_shuffle_on = tk_image_from_file(file_path=shuffle_on_path)
        image_prev_track = tk_image_from_file(file_path=prev_track_path)
        image_play = tk_image_from_file(file_path=play_path)
        image_pause = tk_image_from_file(file_path=pause_path)
        image_next_track = tk_image_from_file(file_path=next_track_path)
        image_repeat_context = tk_image_from_file(file_path=repeat_context_path)
        image_repeat_track = tk_image_from_file(file_path=repeat_track_path)
        image_repeat_off = tk_image_from_file(file_path=repeat_off_path)
        image_add_queue = tk_image_from_file(file_path=add_queue)

        # Player Interactions
        self.player_label = Label(self.mainframe, text='Player:', fg=textcolor, bg=backcolor, font=self.bold_font)
        self.shuffle_button = Button(self.mainframe, image=image_shuffle_off, fg=textcolor, bg=backcolor,
                                     command=lambda: self.change_shuffle_state())
        self.prev_button = Button(self.mainframe, image=image_prev_track, fg=textcolor, bg=backcolor,
                                  command=lambda: self.prev_track())
        self.pause_button = Button(self.mainframe, image=image_pause, fg=textcolor, bg=backcolor,
                                   command=lambda: self.pause())
        self.next_button = Button(self.mainframe, image=image_next_track, fg=textcolor, bg=backcolor,
                                  command=lambda: self.next_track())
        self.repeat_button = Button(self.mainframe, image=image_repeat_off, fg=textcolor, bg=backcolor,
                                    command=lambda: self.new_repeat_state())

        self.progress_label = Label(self.mainframe, text='Progress (sec):', fg=textcolor, bg=backcolor,
                                    font=self.bold_font)
        self.progress_entry = Entry(self.mainframe, fg=textcolor, bg=backcolor, insertbackground='white',
                                    font=self.input_font)
        self.progress_bar = ttk.Progressbar(self.mainframe, length=100, orient='horizontal',
                                            style='design.Horizontal.TProgressbar', variable=self.progress_sec)

        self.volume_label = Label(self.mainframe, text='Volume (%):', fg=textcolor, bg=backcolor, font=self.bold_font)
        # self.volume_entry = Entry(self.mainframe, fg=textcolor, bg=backcolor, insertbackground='white', font=self.input_font)
        self.volume_entry = Scale(self.mainframe, variable=self.current_volume, from_=0, to=100, orient=HORIZONTAL,
                                  command=self.update_volume, fg=textcolor, bg=backcolor, troughcolor=backcolor,
                                  highlightthickness=0, font=self.normal_font)

        # Search Frame
        self.search_entry = Entry(self.mainframe, fg=textcolor, bg=backcolor, insertbackground='white',
                                  font=self.input_font)
        self.current_object_name = Label(self.mainframe, anchor='w', fg=textcolor, bg=backcolor)
        self.current_object_info = Label(self.mainframe, anchor='w', fg=textcolor, bg=backcolor)
        self.current_object_image = Label(self.mainframe, fg=textcolor, bg=backcolor)

        self.current_right_one_button = None
        self.current_false_one_button = None

        # Track Information
        self.track_label = Label(self.mainframe, text='Track:', fg=textcolor, bg=backcolor, font=self.bold_font)
        self.track_name = Label(self.mainframe, fg=textcolor, bg=backcolor, anchor='w')
        self.artist_label = Label(self.mainframe, text='Artist:', fg=textcolor, bg=backcolor, font=self.bold_font)
        self.artist_name = Label(self.mainframe, fg=textcolor, bg=backcolor, anchor='w')
        self.album_label = Label(self.mainframe, text='Album:', fg=textcolor, bg=backcolor, font=self.bold_font)
        self.album_name = Label(self.mainframe, fg=textcolor, bg=backcolor, anchor='w')
        self.image_label = Label(self.mainframe, bg=backcolor)

        # Searched Instance Options
        self.instance_option_1 = Button(self.mainframe, fg=textcolor, bg=backcolor)
        self.instance_option_2 = Button(self.mainframe, fg=textcolor, bg=backcolor)
        self.instance_option_3 = Button(self.mainframe, fg=textcolor, bg=backcolor)
        self.instance_option_4 = Button(self.mainframe, fg=textcolor, bg=backcolor)
        self.instance_option_5 = Button(self.mainframe, fg=textcolor, bg=backcolor)

        self.organize_elements()
        self.update_labels()
        self.bind_entries()
        self.instance_options_buttons()

        master.mainloop()

    # Primary methods:
    def organize_elements(self):
        label_width = 0.075
        entry_width = 0.15
        button_width = 0.08
        label_height = 0.1
        inter_button_width = 0.08
        inter_label_height = 0.05

        track_row_height = 0.575
        player_row1_height = 0.725
        player_row2_height = 0.875
        inter_button_row_height = 0.475

        self.mainframe.place(relwidth=1, relheight=1, relx=0, rely=0)

        # Search Frame
        self.search_entry.place(relwidth=0.6, relheight=label_height, relx=0.2, rely=0.025)
        self.current_object_name.place(relwidth=0.375, relheight=label_height, relx=0.2, rely=0.175)
        self.current_object_info.place(relwidth=0.375, relheight=label_height, relx=0.2, rely=0.325)
        self.current_object_image.place(relwidth=0.125, relheight=0.25, relx=0.6, rely=0.175)

        self.instance_option_1.place(relwidth=inter_button_width, relheight=inter_label_height, relx=0.2,
                                     rely=inter_button_row_height)
        self.instance_option_2.place(relwidth=inter_button_width, relheight=inter_label_height, relx=0.33,
                                     rely=inter_button_row_height)
        self.instance_option_3.place(relwidth=inter_button_width, relheight=inter_label_height, relx=0.46,
                                     rely=inter_button_row_height)
        self.instance_option_4.place(relwidth=inter_button_width, relheight=inter_label_height, relx=0.59,
                                     rely=inter_button_row_height)
        self.instance_option_5.place(relwidth=inter_button_width, relheight=inter_label_height, relx=0.72,
                                     rely=inter_button_row_height)

        # Player Frame
        self.track_label.place(relwidth=label_width, relheight=label_height, relx=0.00625, rely=track_row_height)
        self.track_name.place(relwidth=entry_width, relheight=label_height, relx=0.09375, rely=track_row_height)
        self.artist_label.place(relwidth=label_width, relheight=label_height, relx=0.26875, rely=track_row_height)
        self.artist_name.place(relwidth=entry_width, relheight=label_height, relx=0.35625, rely=track_row_height)
        self.album_label.place(relwidth=label_width, relheight=label_height, relx=0.53125, rely=track_row_height)
        self.album_name.place(relwidth=entry_width, relheight=label_height, relx=0.61875, rely=track_row_height)
        self.image_label.place(relwidth=0.2, relheight=0.4, relx=0.79375, rely=track_row_height)

        self.player_label.place(relwidth=label_width, relheight=label_height, relx=0.00625, rely=player_row1_height)
        self.shuffle_button.place(relwidth=button_width, relheight=label_height, relx=0.13335, rely=player_row1_height)
        self.prev_button.place(relwidth=button_width, relheight=label_height, relx=0.26545, rely=player_row1_height)
        self.pause_button.place(relwidth=button_width, relheight=label_height, relx=0.39755, rely=player_row1_height)
        self.next_button.place(relwidth=button_width, relheight=label_height, relx=0.52965, rely=player_row1_height)
        self.repeat_button.place(relwidth=button_width, relheight=label_height, relx=0.66175, rely=player_row1_height)

        self.progress_label.place(relwidth=entry_width, relheight=label_height, relx=0.05625, rely=player_row2_height)
        self.progress_entry.place(relwidth=0.1125, relheight=label_height * 0.75 - 0.01, relx=0.23125,
                                  rely=player_row2_height)
        self.progress_bar.place(relwidth=0.1125, relheight=label_height * 0.25, relx=0.23125,
                                rely=player_row2_height + label_height * 0.75 + 0.01)
        self.volume_label.place(relwidth=entry_width, relheight=label_height, relx=0.35625, rely=player_row2_height)
        self.volume_entry.place(relwidth=label_width + 0.0125 + entry_width, relheight=label_height, relx=0.53125,
                                rely=player_row2_height)

    def update_progress_bar(self):
        current_progress = self.progress_sec.get()
        progress_bar_total = self.player.current_track.duration

        current_bar_progress = current_progress / progress_bar_total * 100

        if current_bar_progress > 100:
            current_bar_progress = 0

        self.progress_sec.set(self.player.progress)
        self.progress_bar["value"] = current_bar_progress

        # self.mainframe.after(ms=1000, func=self.update_progress_bar(progress_bar_total=progress_bar_total, progress_bar_current=progress_bar_current+1))

    def update_labels(self):
        # Update the Player
        self.player.initialize_player()

        current_track_time = self.player.current_track.duration
        current_progress = self.player.progress

        # Update the text of the labels
        self.track_name.config(text=self.player.current_track.name, font=self.normal_font)
        self.artist_name.config(text=value_from_dict(self.player.current_track.artist), font=self.normal_font)
        self.album_name.config(text=value_from_dict(self.player.current_track.album), font=self.normal_font)

        # Update the track image
        self.get_track_image()

        self.update_progress_bar()  # , progress_bar_current=current_progress)

        # Schedule the next update after the track changes
        self.mainframe.after(current_track_time - current_progress, self.update_labels)

    # Search related methods:
    def search_object(self, event):
        self.instance_options_buttons()

        entered_input = self.search_entry.get()
        if entered_input != '':
            self.search_result_elements()
            self.find_object(entered_input)

    def find_object(self, query_name: str,
                    query_type: Literal['album', 'artist', 'playlist', 'track', 'user', ''] = ''):
        self.yes_button_pressed.set(0)

        def create_search_button():
            self.current_right_one_button = Button(
                self.mainframe,
                text='Y',
                fg=textcolor,
                bg=backcolor,
                font=self.normal_font,
                command=lambda: self.yes_button_pressed.set(1)
            )
            self.current_false_one_button = Button(
                self.mainframe,
                text='N',
                fg=textcolor,
                bg=backcolor,
                font=self.normal_font,
                command=lambda: self.yes_button_pressed.set(2)
            )
            self.current_right_one_button.place(relwidth=0.05, relheight=0.1, relx=0.75, rely=0.175)
            self.current_false_one_button.place(relwidth=0.05, relheight=0.1, relx=0.75, rely=0.325)
            self.search_buttons_needed.set(True)

        def destroy_search_buttons():
            if self.search_buttons_needed.get():
                self.current_right_one_button.destroy()
                self.current_false_one_button.destroy()

        def choose_if_right():
            create_search_button()
            self.mainframe.wait_variable(self.yes_button_pressed)
            if self.yes_button_pressed.get() == 1:
                destroy_search_buttons()
                return True
            else:
                return False

        def current_object_instance() -> Union[Album, Artist, Playlist, Track]:
            if re.search("album", next(iter(results.keys())), re.IGNORECASE) is not None:
                return Album(current_object['id'])

            elif re.search("artist", next(iter(results.keys())), re.IGNORECASE) is not None:
                return Artist(current_object['id'])

            elif re.search("playlist", next(iter(results.keys())), re.IGNORECASE) is not None:
                return Playlist(current_object['id'])

            elif re.search("track", next(iter(results.keys())), re.IGNORECASE) is not None:
                return Track(current_object['id'])

        if query_type == '':
            if re.search('album', query_name, re.IGNORECASE) is not None:
                query_type = 'album'
            elif re.search('artist', query_name, re.IGNORECASE) is not None:
                query_type = 'artist'
            elif re.search('playlist', query_name, re.IGNORECASE) is not None:
                query_type = 'playlist'
            elif re.search('track', query_name, re.IGNORECASE) is not None:
                query_type = 'track'
            elif re.search('user', query_name, re.IGNORECASE) is not None:
                query_type = 'user'

            query_name = re.sub(query_type, '', query_name)

        if query_type == '':
            results = self.sp.search(q=query_name, market=MARKET, limit=50)
        else:
            results = self.sp.search(q=query_name, type=query_type, market=MARKET, limit=50)

        for current_object in results[next(iter(results.keys()))]['items']:

            current_instance = current_object_instance()
            self.current_object_name.config(text=current_instance.name, font=self.normal_font)
            match current_instance.instance['type']:
                case 'album':
                    self.current_object_info.config(text=value_from_dict(current_instance.artist),
                                                    font=self.normal_font)
                case 'artist':
                    self.current_object_info.config(text='', font=self.normal_font)
                case 'playlist':
                    self.current_object_info.config(text=current_instance.owner.name, font=self.normal_font)
                case 'track':
                    self.current_object_info.config(
                        text=value_from_dict(current_instance.album) + ', ' + value_from_dict(
                            current_instance.artist),
                        font=self.normal_font)
            global current_image
            current_image = get_tk_image(current_instance.image, [100, 100])
            self.current_object_image.config(image=current_image)

            self.organize_elements()
            self.instance_options_buttons()

            decision = choose_if_right()
            if decision:
                self.search_entry.delete(0, END)
                self.new_instance_options(current_instance)
                return current_instance

    def search_result_elements(self, new_instance=None):
        if new_instance is None:
            self.current_object_name.place_forget()
            self.current_object_info.place_forget()
            self.current_object_info.place_forget()

        else:
            self.organize_elements()

    def instance_options_buttons(self, new_instance: Union[Track, None] = None) -> None:
        if new_instance is None:
            self.instance_option_1.place_forget()
            self.instance_option_2.place_forget()
            self.instance_option_3.place_forget()
            self.instance_option_4.place_forget()
            self.instance_option_5.place_forget()
            self.instance_option_buttons_needed.set(True)

        else:
            self.organize_elements()
            self.instance_option_buttons_needed.set(False)

    def new_instance_options(self, new_instance: Union[Album, Artist, Playlist, Track]):

        def searched_album_options():
            self.instance_option_1.config(text='', command=lambda: self.not_implemented())
            self.instance_option_2.config(text='', command=lambda: self.not_implemented())
            self.instance_option_3.config(text='', command=lambda: self.not_implemented())
            self.instance_option_4.config(text='', command=lambda: self.not_implemented())
            self.instance_option_5.config(text='', command=lambda: self.not_implemented())

        def searched_artist_options():
            self.instance_option_1.config(text='', command=lambda: self.not_implemented())
            self.instance_option_2.config(text='', command=lambda: self.not_implemented())
            self.instance_option_3.config(text='like', command=lambda: self.not_implemented())
            self.instance_option_4.config(text='hate', command=lambda: self.not_implemented())
            self.instance_option_5.config(text='', command=lambda: self.not_implemented())

        def searched_playlist_options():
            self.instance_option_1.config(image=image_play, command=lambda: self.not_implemented())
            self.instance_option_2.config(image=image_add_queue, command=lambda: self.not_implemented())
            self.instance_option_3.config(text='like', command=lambda: self.not_implemented())
            self.instance_option_4.config(text='hate', command=lambda: self.not_implemented())
            self.instance_option_5.config(text='', command=lambda: self.not_implemented())

        def searched_track_options():
            self.instance_option_1.config(image=image_play, command=lambda: self.not_implemented())
            self.instance_option_2.config(image=image_add_queue, command=lambda: self.add_track_to_queue(new_instance))
            self.instance_option_3.config(text='like', command=lambda: self.add_track_to_favourites(new_instance))
            self.instance_option_4.config(text='hate', command=lambda: self.add_track_to_blacklist(new_instance))
            self.instance_option_5.config(text='', command=lambda: self.not_implemented())

        if isinstance(new_instance, Album):
            searched_album_options()
        elif isinstance(new_instance, Artist):
            searched_artist_options()
        elif isinstance(new_instance, Playlist):
            searched_playlist_options()
        elif isinstance(new_instance, Track):
            searched_track_options()

        self.instance_options_buttons(new_instance)

    def not_implemented(self):
        print("Not implemented")

    def play_track(self, track: Track):
        pass

    def add_track_to_queue(self, track: Track):
        self.sp.add_to_queue(track.id, self.player.device.id)

    def add_track_to_favourites(self, track: Track):
        self.sp.current_user_saved_tracks_add([track.id])

    def track_tbn_method(self):
        pass

    def add_track_to_blacklist(self, track: Track):
        track.is_blacklisted = 1

    # Player related methods:
    def bind_entries(self):
        # Bind the Return/Enter key to the process_command function
        self.progress_entry.bind("<Return>", self.update_progress)
        # self.volume_entry.bind("<Return>", self.update_volume)
        self.search_entry.bind("<Return>", self.search_object)

    def new_repeat_state(self):
        match self.player.repeat_state:
            case "context":
                self.player.change_repeat_state('track')
                self.repeat_button.config(image=image_repeat_track)
            case "track":
                self.player.change_repeat_state('off')
                self.repeat_button.config(image=image_repeat_off)
            case "off":
                self.player.change_repeat_state('context')
                self.repeat_button.config(image=image_repeat_context)

        self.player.initialize_player()
        self.repeat_state = self.player.repeat_state

    def prev_track(self):
        self.player.prev_track()
        self.update_labels()

    def pause(self):
        self.player.change_playing_state()
        if self.player.is_playing:
            self.pause_button.config(image=image_play)
        else:
            self.pause_button.config(image=image_pause)
        self.update_labels()

    def next_track(self):
        self.player.next_track()
        self.update_labels()

    def change_shuffle_state(self):
        self.player.change_shuffle_state()
        if self.player.shuffle_state:
            self.shuffle_button.config(image=image_shuffle_on)
        else:
            self.shuffle_button.config(image=image_shuffle_off)

    def update_progress(self, event):
        new_progress = self.progress_entry.get()
        self.progress_entry.delete(0, END)
        self.player.set_progress(int(new_progress))
        self.update_progress_bar()
        self.update_labels()

    def update_volume(self, event):
        new_volume = self.volume_entry.get()
        # self.volume_entry.delete(0, END)
        self.player.set_volume(int(new_volume))

    def update_search(self, event):
        new_search = self.search_entry.get()
        self.find_object(new_search)

    def get_track_image(self):
        global track_image
        track_image = get_tk_image(self.player.current_track.image, [200, 200])
        self.image_label.config(image=track_image)


if __name__ == '__main__':
    def start_window():
        try:
            SpotifyAppWindow()
        except requests.exceptions.ConnectionError as connection_error:
            print("Spotify went mimimi")
            return start_window


