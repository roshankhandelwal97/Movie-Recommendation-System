#importing the necessary libraries

import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import tkinter as tk
from tkinter import ttk, messagebox


#list to store the predicted rating values of the animes
predictions = []

# Load anime and rating data
anime_df = pd.read_csv('anime.csv')
rating_df = pd.read_csv('rating.csv')



# Data preprocessing by Replacing -1 ratings with NaN
rating_df = rating_df.replace({-1: float('nan')})


#Autocomple Feature
class EntryAutocomplete(ttk.Entry):
    def __init__(self, parent, autocomplete_list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.var = self["textvariable"]
        if self.var == "":
            self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == "":
            if self.lb_up:
                self.lb.destroy()
                self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox(self.master)
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True
                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = 0
            else:
                index = self.lb.curselection()[0]
            if index > 0:
                self.lb.selection_clear(first=index)
                index -= 1
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = 0
            else:
                index = self.lb.curselection()[0]
            if index < self.lb.size() - 1:
                self.lb.selection_clear(first=index)
                index += 1
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        return [w for w in self.autocomplete_list if w.lower().startswith(self.var.get().lower())]



def display_recommendations(sort_by=None):

    global predictions

    # Display top 10 anime recommendations in the UI
    top_animes = []
    for i in range(10):
        anime_id = predictions[i].iid
        anime_data = anime_df[anime_df['anime_id'] == anime_id]
        anime_name = anime_data['name'].values[0]
        anime_episodes = anime_data['episodes'].values[0]
        anime_members = anime_data['members'].values[0]
        top_animes.append({'name': anime_name, 'episodes': anime_episodes, 'members': anime_members})

    if sort_by:
        top_animes = sorted(top_animes, key=lambda x: x[sort_by], reverse=True)

    result_text = "Top 10 anime recommendations for you:\n"
    for i, anime in enumerate(top_animes):
        result_text += f"{i+1}. {anime['name']}\n"

    result_label.config(text=result_text)
    

#Function to sort the predicted anime list in the order of number of episodes
def sort_by_episodes():
    display_recommendations(sort_by='episodes')


#Function to sort the predicted anime list in the order of number of members who have seen it
def sort_by_members():
    display_recommendations(sort_by='members')


#Function to update the progress bar value
def update_progress(value):
    progress_bar["value"] = value
    progress_percentage.set(f"{value}%")
    root.update_idletasks()

#Function to hide the progress bar once the prediction is made
def hide_progress():
    progress_bar.grid_forget()
    progress_percentage_label.grid_forget()


#Function to check if any of the input field is left blank by a user
def validate_input(anime_list, rating_list):
    for i, (anime, rating) in enumerate(zip(anime_list, rating_list)):
        if not anime.strip():
            messagebox.showerror("Input Error", f"Please enter an anime name for Favorite Anime {i + 1}.")
            return False
        if not rating.strip():
            messagebox.showerror("Input Error", f"Please enter a rating for Favorite Anime {i + 1}.")
            return False
    return True


#Function which runs the main algorithm and provides the list of predicted animes
def submit_ratings():

    global predictions

    # Load anime and rating data
    anime_df = pd.read_csv('anime.csv')
    rating_df = pd.read_csv('rating.csv')

    # Replace -1 ratings with NaN
    rating_df = rating_df.replace({-1: float('nan')})   


    # Get user input from the UI
    anime_list = [entry_anime1.get(), entry_anime2.get(), entry_anime3.get()]
    rating_list = [entry_rating1.get(), entry_rating2.get(), entry_rating3.get()]

    # Validate user input
    if not validate_input(anime_list, rating_list):
        return

    # Update progress bar
    update_progress(10)


    # Create user rating dataframe
    user_id = rating_df['user_id'].max() + 1
    update_progress(20)
    anime_input = anime_df[anime_df['name'].isin(anime_list)].reset_index(drop=True)
    update_progress(25)
    user_ratings = pd.DataFrame({'user_id': [user_id]*len(anime_input), 'anime_id': anime_input['anime_id'], 'rating': [float(rating) for rating in rating_list[:len(anime_input)]]})

    # Append user input to rating dataframe
    rating_df = pd.concat([rating_df, user_ratings], ignore_index=True)

    # Update progress bar
    update_progress(30)

    # Replace NaN values with 0
    rating_df['rating'] = rating_df['rating'].fillna(0)

    # Replace 0 ratings with mean rating of the user
    rating_df['rating'] = rating_df.groupby('user_id')['rating'].transform(lambda x: x.replace(0, x.mean()).astype(int))

    update_progress(40)

    # Create Surprise dataset and train-test split
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(rating_df[['user_id', 'anime_id', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.25)

    # Update progress bar
    update_progress(50)

    # Train the model
    model = SVD()
    update_progress(65)
    model.fit(trainset)

    # Update progress bar
    update_progress(70)

    # Get list of all anime ids and remove those already rated by the user
    anime_ids = [anime_id for anime_id in rating_df['anime_id'].unique() if anime_id not in anime_input['anime_id'].unique()]
    update_progress(80)

    # Predict ratings for remaining anime ids and sort them by estimated rating (highest first)
    predictions = sorted([model.predict(user_id, anime_id) for anime_id in anime_ids], key=lambda x: x.est, reverse=True)

    update_progress(90)

    # Update progress bar
    update_progress(95)

    # Display top 10 anime recommendations in the UI
    result_text = "Top 10 anime recommendations for you:\n"
    for i in range(10):
        anime_id = predictions[i].iid
        anime_name = anime_df[anime_df['anime_id'] == anime_id]['name'].values[0]
        result_text += f"{i+1}. {anime_name}\n"
    result_label.config(text=result_text)
    
    update_progress(100)
    hide_progress()

# Create the tkinter UI
root = tk.Tk()
root.title("Anime Recommendation")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input fields for user's favorite anime and ratings
label_anime1 = ttk.Label(frame, text="Favorite Anime 1:")
label_anime1.grid(row=0, column=0, sticky=tk.W)
entry_anime1 = EntryAutocomplete(frame, anime_df['name'].tolist())
entry_anime1.grid(row=0, column=1)

label_rating1 = ttk.Label(frame, text="Rating:")
label_rating1.grid(row=0, column=2, sticky=tk.W)
entry_rating1 = ttk.Entry(frame)
entry_rating1.grid(row=0, column=3)

label_anime2 = ttk.Label(frame, text="Favorite Anime 2:")
label_anime2.grid(row=1, column=0, sticky=tk.W)
entry_anime2 = EntryAutocomplete(frame, anime_df['name'].tolist())
entry_anime2.grid(row=1, column=1)

label_rating2 = ttk.Label(frame, text="Rating:")
label_rating2.grid(row=1, column=2, sticky=tk.W)
entry_rating2 = ttk.Entry(frame)
entry_rating2.grid(row=1, column=3)

label_anime3 = ttk.Label(frame, text="Favorite Anime 3:")
label_anime3.grid(row=2, column=0, sticky=tk.W)
entry_anime3 = EntryAutocomplete(frame, anime_df['name'].tolist())
entry_anime3.grid(row=2, column=1)

label_rating3 = ttk.Label(frame, text="Rating:")
label_rating3.grid(row=2, column=2, sticky=tk.W)
entry_rating3 = ttk.Entry(frame)
entry_rating3.grid(row=2, column=3)

# Submit button
submit_button = ttk.Button(frame, text="Submit Ratings", command=submit_ratings)
submit_button.grid(row=3, column=1, columnspan=2)

# Progress bar
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=4, pady=10)

# Progress percentage
progress_percentage = tk.StringVar()
progress_percentage_label = ttk.Label(frame, textvariable=progress_percentage)
progress_percentage_label.grid(row=5, column=0, columnspan=4)

# Result label
result_label = ttk.Label(frame, text="")
result_label.grid(row=4, column=0, columnspan=4, pady=10)

# Sort recommendations buttons
sort_episodes_button = ttk.Button(frame, text="Sort by Episodes", command=sort_by_episodes)
sort_episodes_button.grid(row=6, column=0, pady=10)

sort_members_button = ttk.Button(frame, text="Sort by Members", command=sort_by_members)
sort_members_button.grid(row=6, column=3, pady=10)

root.mainloop()