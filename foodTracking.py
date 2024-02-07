# AUTHOR: Will Garlington
# Class: CPSC 321, Dr. Bowers
# Org.: Gonzaga U.
# Last Modified: 12.15.2023
# Description: Meal Tracking program that connects to school database.
#       Allows users to track their food intake and compare to stated goals.
#

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import datetime

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MariaDB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # Fetch all results
        results = cursor.fetchall()
        connection.commit()
        cursor.close()
        return results
    except Error as e:
        print(f"The error '{e}' occurred")
        cursor.close()
        return None  # explicitly return None
    
def query_database():
    query = entry.get()
    results = execute_query(connection, query)
    if results is not None:
        listbox.delete(0, tk.END)  # clear existing items
        for row in results:
            listbox.insert(tk.END, row)
    else:
        messagebox.showerror("Error", "error occurred while executing query")

def get_user_id(connection, user_name):
    query = f"SELECT u_id FROM user WHERE u_name = '{user_name}'"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        cursor.close()
        return None
    
def add_user(connection, user_name):
    insert_query = f"INSERT INTO user (u_name) VALUES ('{user_name}')"
    cursor = connection.cursor()
    try:
        cursor.execute(insert_query)
        connection.commit()
        print(f"User '{user_name}' added successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()

class MealTrack(tk.Tk):
    def __init__(self, user_name, user_id):
        tk.Tk.__init__(self)
        self.title("MEAL-TRACK")

        # container for all frames
        self.geometry("630x600") # sets size
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        # user vars for passing to other pages
        self.user_name = user_name
        self.user_id = user_id
        self.frames = {}

        # initialize all pages with user data passed to them
        self.frames[StartPage] = StartPage(parent=self.container, controller=self, user_name=user_name, user_id=user_id)
        self.frames[StartPage].grid(row=0, column=0, sticky="nsew")

        self.frames[FoodPage] = FoodPage(parent=self.container, controller=self, user_id=user_id)
        self.frames[FoodPage].grid(row=0, column=0, sticky="nsew")

        self.frames[StatsPage] = StatsPage(parent=self.container, controller=self, user_id=user_id)
        self.frames[StatsPage].grid(row=0, column=0, sticky="nsew")

        self.frames[FoodInfoPage] = FoodInfoPage(parent=self.container, controller=self, user_id=user_id)
        self.frames[FoodInfoPage].grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if cont == StatsPage:
            frame.refresh_data()
        frame.tkraise()

    @staticmethod
    def get_current_date_formatted():
        current_date = datetime.date.today() # gets date
        formatted_date = current_date.strftime("%Y-%m-%d") # Format the date as 'YYYY-MM-DD' for ease of use
        return formatted_date

class StartPage(tk.Frame):
    def __init__(self, parent, controller, user_name, user_id):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # display username and user_id in the corner
        user_info_label = tk.Label(self, text=f"Username: {user_name}\nUser ID: {user_id}", anchor='e', justify=tk.RIGHT, font=("Helvetica", 14))
        user_info_label.grid(row=0, column=1, sticky='ne', padx=10, pady=10)
        
        # display meal track at top
        meal_track_label = tk.Label(self, text="Meal Track", font=("Helvetica", 18))
        meal_track_label.grid(row=1, column=0, padx=10, pady=10)

        # buttons for seperate pages
        button1 = tk.Button(self, text="New Food", command=lambda: controller.show_frame(FoodPage))
        button1.grid(row=2, column=0, padx=10, pady=10)

        button2 = tk.Button(self, text="Stats", command=lambda: controller.show_frame(StatsPage))
        button2.grid(row=3, column=0, padx=10, pady=10)

        button3 = tk.Button(self, text="Food Information", command=lambda: controller.show_frame(FoodInfoPage))
        button3.grid(row=4, column=0, padx=10, pady=10)

class FoodPage(tk.Frame):
    def __init__(self, parent, controller, user_id):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_id = user_id

        # filter label
        filter_label = tk.Label(self, text="Filter")
        filter_label.grid(row=0, column=0, padx=10, pady=10)

        # filter dropdown
        self.filter_dropdown = ttk.Combobox(self)
        self.filter_dropdown.grid(row=0, column=1, padx=10)

        # filter apply button
        apply_button = tk.Button(self, text="Apply", command=self.apply_filter)
        apply_button.grid(row=0, column=2, padx=10)

        # food label
        food_info_label = tk.Label(self, text="Food")
        food_info_label.grid(row=1, column=0, padx=10, pady=10)

        # food dropdown
        self.food_dropdown = ttk.Combobox(self)
        self.food_dropdown.grid(row=1, column=1, padx=10)

        # label for amount
        amount_label = tk.Label(self, text="Amount (oz)")
        amount_label.grid(row=2, column=0, padx=10, pady=10)

        # amount slider
        self.amount_scale = tk.Scale(self, from_=0, to=32, orient=tk.HORIZONTAL)
        self.amount_scale.grid(row=2, column=1, padx=10, pady=10)
        
        # add-food button
        add_food_button = tk.Button(self, text="Add Food", command=self.add_food)
        add_food_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # return button
        back_button = tk.Button(self, text="Back to Start Page", command=lambda: controller.show_frame(StartPage))
        back_button.grid(row=4, column=0, columnspan=2, pady=10)

        # calls functions to populate dropdown menus on open
        self.populate_food_dropdown()
        self.populate_filter_dropdown()

    # pulls food names for display in dropdown
    def populate_food_dropdown(self, classification=None):
        if classification:
            # if filter is applied then run with filter
            query = f"SELECT name FROM food_info WHERE classification = '{classification}'"
        else:
            query = "SELECT name FROM food_info"
        results = execute_query(connection, query)
        if results is not None:
            food_names = [item[0] for item in results]
            self.food_dropdown['values'] = food_names
        else:
            messagebox.showerror("Error", "An error occurred while fetching food names")

    # gets classifications for filter menu
    def populate_filter_dropdown(self):
        query = "SELECT classification FROM food_info GROUP BY classification"
        results = execute_query(connection, query)
        if results is not None:
            classifications = [item[0] for item in results]
            self.filter_dropdown['values'] = classifications
        else:
            messagebox.showerror("Error", "An error occurred while fetching classifications")

    def apply_filter(self):
        selected_classification = self.filter_dropdown.get()
        self.populate_food_dropdown(selected_classification)
    
    def add_food(self):
        # gets selected food
        selected_food = self.food_dropdown.get()
        # get selected food id
        query = f"SELECT food_id FROM food_info WHERE name = '{selected_food}'"
        result = execute_query(connection, query)
        if result:
            food_id = result[0][0]  # gets first result (hopefully id)
            amount = self.amount_scale.get()  # get amount
            current_date = MealTrack.get_current_date_formatted()  # fetch date
            user_id = self.user_id

            # checks to ensure no duplicate entries
            check_query = f"SELECT amount FROM food_by_day WHERE date = '{current_date}' AND u_id = {user_id} AND food_id = {food_id}"
            check_result = execute_query(connection, check_query)
            
            if check_result:
                # if already in table, adds amount to existing total
                existing_amount = check_result[0][0]
                new_amount = existing_amount + amount
                update_query = f"UPDATE food_by_day SET amount = {new_amount} WHERE date = '{current_date}' AND u_id = {user_id} AND food_id = {food_id}"
                execute_query(connection, update_query)
                messagebox.showinfo("Success", "food amount updated")
            else:
                # insert new if not in table already
                insert_query = f"INSERT INTO food_by_day VALUES ('{current_date}', {user_id}, {food_id}, {amount})"
                execute_query(connection, insert_query)
                messagebox.showinfo("Success", "food added successfully")
        else:
            messagebox.showerror("Error", "food not in database")

class StatsPage(tk.Frame):
    def __init__(self, parent, controller, user_id):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_id = user_id

        # stats page label
        label = tk.Label(self, text="Stats", font=("Helvetica", 16))
        label.pack(pady=10, padx=10)

        self.stats_container = tk.Frame(self)
        self.stats_container.pack(pady=10)

        # parts for displaying food and the delete button
        self.results_section = tk.Frame(self.stats_container)
        self.results_section.pack(side=tk.LEFT, padx=10)

        self.results_listbox = tk.Listbox(self.results_section)
        self.results_listbox.pack(pady=10)

        self.remove_food_button = tk.Button(self.results_section, text="Remove Food", command=self.remove_food)
        self.remove_food_button.pack(pady=10)

        # parts for Todays Totals section
        self.totals_section = tk.Frame(self.stats_container)
        self.totals_section.pack(side=tk.LEFT, padx=10)

        self.totals_label = tk.Label(self.totals_section, text="Today's Totals:", font=("Helvetica", 12))
        self.totals_label.pack()

        self.nutrition_label = tk.Label(self.totals_section, text="", font=("Helvetica", 12))
        self.nutrition_label.pack(pady=10, padx=10)

        # parts for user goals section
        self.goals_section = tk.Frame(self.stats_container)
        self.goals_section.pack(side=tk.LEFT, padx=10)

        self.goals_label = tk.Label(self.goals_section, text="Your Goals:", font=("Helvetica", 12))
        self.goals_label.pack()

        self.user_goals_label = tk.Label(self.goals_section, text="", font=("Helvetica", 12))
        self.user_goals_label.pack()

        self.change_goals_button = tk.Button(self.goals_section, text="Change Goals", command=self.change_goals)
        self.change_goals_button.pack(pady=10)

        # parts for leaderboard display
        self.leaderboard_section = tk.Frame(self.goals_section)
        self.leaderboard_section.pack(pady=10)
        
        leaderboard_label = tk.Label(self.leaderboard_section, text="Leaderboard", font=("Helvetica", 12))
        leaderboard_label.pack()

        # labels for places 1-3
        self.first_place_label = tk.Label(self.leaderboard_section, text="1st Place: ", font=("Helvetica", 10))
        self.first_place_label.pack()

        self.second_place_label = tk.Label(self.leaderboard_section, text="2nd Place: ", font=("Helvetica", 10))
        self.second_place_label.pack()

        self.third_place_label = tk.Label(self.leaderboard_section, text="3rd Place: ", font=("Helvetica", 10))
        self.third_place_label.pack()

        # back button + padding
        back_button = tk.Button(self, text="Back to Start Page", command=lambda: controller.show_frame(StartPage))
        back_button.pack(pady=10)

        # populates data when page is opened
        self.load_data()
        self.load_user_goals()
        self.load_leaderboard()  # call to load leaderboard data

    # fetches data for user total
    def load_data(self):
        current_date = MealTrack.get_current_date_formatted()

        query = f"SELECT food_id, SUM(amount) FROM food_by_day WHERE date = '{current_date}' AND u_id = {self.user_id} GROUP BY food_id"
        results = execute_query(connection, query)

        total_calories = total_protein = total_fat = total_carbs = total_sugars = total_fiber = 0.0 # declare vars

        if results:
            # this block adds together all the foods to derive daily totals
            for food_id, total_amount in results:
                nutrition_query = f"SELECT calorie, protein, fat, carb, sugar, fiber FROM food_stats WHERE food_id = {food_id}"
                nutrition_result = execute_query(connection, nutrition_query)
                if nutrition_result:
                    calorie, protein, fat, carb, sugar, fiber = nutrition_result[0]
                    total_calories += calorie * total_amount
                    total_protein += protein * total_amount
                    total_fat += fat * total_amount
                    total_carbs += carb * total_amount
                    total_sugars += sugar * total_amount
                    total_fiber += fiber * total_amount

            # update nutrition label
            self.nutrition_label.config(text=f"Calories: {round(total_calories, 2)}\nProtein: {round(total_protein, 2)}g\nFat: {round(total_fat, 2)}g\nCarbs: {round(total_carbs, 2)}g\nSugars: {round(total_sugars, 2)}g\nFiber: {round(total_fiber, 2)}g")

            # check if user already has entry for today
            check_query = f"SELECT * FROM user_day WHERE u_id = {self.user_id} AND date = '{current_date}'"
            check_result = execute_query(connection, check_query)

            if check_result:
                # update entry to new vals
                update_query = f"UPDATE user_day SET cal_tot = {total_calories}, pro_tot = {total_protein}, fat_tot = {total_fat}, car_tot = {total_carbs}, sug_tot = {total_sugars}, fib_tot = {total_fiber} WHERE u_id = {self.user_id} AND date = '{current_date}'"
            else:
                # create new entry for today
                update_query = f"INSERT INTO user_day VALUES ({self.user_id}, '{current_date}', {total_calories}, {total_protein}, {total_fat}, {total_carbs}, {total_sugars}, {total_fiber})"
            
            execute_query(connection, update_query)
        else:
            self.nutrition_label.config(text="No food data for today")
    
    # fetches data for todays food list
    def load_list(self):
        current_date = MealTrack.get_current_date_formatted()
        query = f"SELECT food_id, SUM(amount) FROM food_by_day WHERE date = '{current_date}' AND u_id = {self.user_id} GROUP BY food_id"
        results = execute_query(connection, query)
        if results:
            for food_id, total_amount in results:
                # get food names for the all ids
                food_name_query = f"SELECT name FROM food_info WHERE food_id = {food_id}"
                food_name_result = execute_query(connection, food_name_query)
                if food_name_result:
                    food_name = food_name_result[0][0]
                    display_text = f"{food_name}: {total_amount} oz"
                    self.results_listbox.insert(tk.END, display_text)
                else:
                    self.results_listbox.insert(tk.END, f"unknown food id: {food_id}")
        else:
            self.results_listbox.insert(tk.END, "No data for today")
    
    # controls delete food button
    def remove_food(self):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)
            # get food_id and amount from the selected item
            food_name, amount = selected_item.split(': ')
            amount = float(amount.split(' ')[0])  # get the amount (before ' oz')

            # find food_id with name
            query = f"SELECT food_id FROM food_info WHERE name = '{food_name}'"
            result = execute_query(connection, query)
            if result:
                food_id = result[0][0]

                # delete tuple for selected food
                current_date = MealTrack.get_current_date_formatted()
                delete_query = f"DELETE FROM food_by_day WHERE u_id = {self.user_id} AND date = '{current_date}' AND food_id = {food_id} AND amount = {amount}"
                execute_query(connection, delete_query)

                # refresh the list
                self.refresh_data()

            else:
                messagebox.showwarning("Warning", "selected food not found")
        else:
            messagebox.showwarning("Warning", "no food selected")

    # loads user goals
    def load_user_goals(self):
        # query for goals
        goal_query = f"SELECT cal_goal, pro_goal, fat_goal, car_goal, sug_goal, fib_goal FROM user_goal WHERE u_id = {self.user_id}"
        goal_results = execute_query(connection, goal_query)
        if goal_results:
            # set texts to fetched goals
            cal_goal, pro_goal, fat_goal, car_goal, sug_goal, fib_goal = goal_results[0]
            goals_text = f"Calories: {cal_goal}\nProtein: {pro_goal}g\nFat: {fat_goal}g\nCarbs: {car_goal}g\nSugars: {sug_goal}g\nFiber: {fib_goal}g"
            self.user_goals_label.config(text=goals_text)
        else:
            self.user_goals_label.config(text="No goal data available.")

    def change_goals(self):
        # promts for all goals
        new_cal_goal = simpledialog.askfloat("Input", "Enter new calorie goal:", parent=self)
        new_pro_goal = simpledialog.askfloat("Input", "Enter new protein goal (g):", parent=self)
        new_fat_goal = simpledialog.askfloat("Input", "Enter new fat goal (g):", parent=self)
        new_car_goal = simpledialog.askfloat("Input", "Enter new carb goal (g):", parent=self)
        new_sug_goal = simpledialog.askfloat("Input", "Enter new sugar goal (g):", parent=self)
        new_fib_goal = simpledialog.askfloat("Input", "Enter new fiber goal (g):", parent=self)

        if None not in (new_cal_goal, new_pro_goal, new_fat_goal, new_car_goal, new_sug_goal, new_fib_goal):
            # update database
            update_query = f"""
                UPDATE user_goal 
                SET cal_goal = {new_cal_goal}, pro_goal = {new_pro_goal}, 
                    fat_goal = {new_fat_goal}, car_goal = {new_car_goal}, 
                    sug_goal = {new_sug_goal}, fib_goal = {new_fib_goal} 
                WHERE u_id = {self.user_id}
            """
            execute_query(connection, update_query)
            messagebox.showinfo("Success", "goals updated")
            self.load_user_goals()  # refresh goals
        else:
            messagebox.showwarning("Warning", "all goals must be set")

    def load_leaderboard(self):
        # query to get total days logged for all users
        user_query = "SELECT u_id, COUNT(*) FROM user_day GROUP BY u_id;"
        user_results = execute_query(connection, user_query)

        success_rates = {}

        for user_id, total_days in user_results:
            # query for number of days where goals are met
            goal_met_query = f"""
                SELECT COUNT(*) FROM user_day 
                WHERE u_id = {user_id} AND cal_tot >= (SELECT cal_goal FROM user_goal WHERE u_id = {user_id})
            """
            goal_met_results = execute_query(connection, goal_met_query)
            if goal_met_results:
                # creates percent success rate for reaching goals
                days_goal_met = goal_met_results[0][0]
                success_rate = days_goal_met / total_days if total_days > 0 else 0
                success_rates[user_id] = success_rate

        # sort users by success rate
        top_users = sorted(success_rates.items(), key=lambda x: x[1], reverse=True)[:3] # :3 haha

        places = ["1st Place: ", "2nd Place: ", "3rd Place: "]
        labels = [self.first_place_label, self.second_place_label, self.third_place_label]

        for i, (user_id, rate) in enumerate(top_users):
            # get username for display
            name_query = f"SELECT u_name FROM user WHERE u_id = {user_id}"
            name_result = execute_query(connection, name_query)
            if name_result:
                user_name = name_result[0][0]
                labels[i].config(text=f"{places[i]}{user_name} - Success Rate: {rate:.2f}")
            else:
                labels[i].config(text=f"{places[i]}User ID {user_id} - Success Rate: {rate:.2f}")
        
        # in case less than three users
        for j in range(i + 1, 3):
            labels[j].config(text=f"{places[j]}N/A")

    # refreshes important data between opens
    def refresh_data(self):
        self.results_listbox.delete(0, tk.END)
        self.load_data()
        self.load_list()

class FoodInfoPage(tk.Frame):
    def __init__(self, parent, controller, user_id):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_id = user_id

        label = tk.Label(self, text="Food Information", font=("Helvetica", 18))
        label.pack(pady=10, padx=10)

        # label for search bar set
        search_by_macros_label = tk.Label(self, text="Search By Macros")
        search_by_macros_label.pack(pady=(0, 5))  # Added padding for visual spacing

        # macro search bars
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)

        # vars for search bar entries
        self.cal_entry = self.create_search_bar(search_frame, "Calories")
        self.pro_entry = self.create_search_bar(search_frame, "Protein")
        self.fat_entry = self.create_search_bar(search_frame, "Fat")
        self.carb_entry = self.create_search_bar(search_frame, "Carbs")
        self.sug_entry = self.create_search_bar(search_frame, "Sugars")
        self.fib_entry = self.create_search_bar(search_frame, "Fiber")

        # search button
        self.search_button = tk.Button(self, text="Search", command=self.perform_search)
        self.search_button.pack(pady=5)

        # box for displaying food info
        self.food_info_listbox = tk.Listbox(self, width=50, height=15)
        self.food_info_listbox.pack(pady=10)

        self.populate_food_info_listbox()

        # back button
        button = tk.Button(self, text="Back to Start Page", command=lambda: controller.show_frame(StartPage))
        button.pack(pady=10)

    # makes search bars
    def create_search_bar(self, parent, label_text):
        label = tk.Label(parent, text=label_text)
        label.pack(side=tk.LEFT)
        entry = tk.Entry(parent, width=8)
        entry.pack(side=tk.LEFT, padx=2)
        return entry  # Return the entry widget

    # fills food box with all foods
    def populate_food_info_listbox(self):
        query = "SELECT name, description FROM food_info ORDER BY classification DESC, name ASC;"
        results = execute_query(connection, query)
        if results:
            for name, description in results:
                display_text = f"{name}: {description}"
                self.food_info_listbox.insert(tk.END, display_text)
        else:
            self.food_info_listbox.insert(tk.END, "No food information available.")

    # handles the earch button click
    def perform_search(self):
        cal_search = self.cal_entry.get() or "0"
        pro_search = self.pro_entry.get() or "0"
        fat_search = self.fat_entry.get() or "0"
        carb_search = self.carb_entry.get() or "0"
        sug_search = self.sug_entry.get() or "0"
        fib_search = self.fib_entry.get() or "0"
        
        # debug
        print(f"Calories: {cal_search}, Protein: {pro_search}, Fat: {fat_search}, Carbs: {carb_search}, Sugars: {sug_search}, Fiber: {fib_search}")

        # looks for food that fit criteria
        query = f"""
            SELECT food_id FROM food_stats 
            WHERE calorie >= {cal_search} AND protein >= {pro_search} 
            AND fat >= {fat_search} AND carb >= {carb_search} 
            AND sugar >= {sug_search} AND fiber >= {fib_search}"""
        print(query)
        food_ids_results = execute_query(connection, query)

        self.food_info_listbox.delete(0, tk.END)  # clear box before new results

        if food_ids_results:
            for (food_id,) in food_ids_results:
                # fetch names from food ids
                name_query = f"SELECT name FROM food_info WHERE food_id = {food_id}"
                name_result = execute_query(connection, name_query)
                if name_result:
                    for (name,) in name_result:
                        self.food_info_listbox.insert(tk.END, name)
        else:
            self.food_info_listbox.insert(tk.END, "No matching foods found.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # hide main window
    user_name = simpledialog.askstring("Input", "What's your name?", parent=root)
    root.deiconify()  # unhide window

    if not user_name:
        messagebox.showinfo("No Name Provided", "No name was provided. Exiting application.")
        root.destroy()
    else:
        print(user_name)
        # create a connection to the database
        connection = create_connection("cps-database.gonzaga.edu", "#DB_USER#", "#PASSWORD#", "#DB_NAME#")
        user_id = get_user_id(connection, user_name) # fetches user_id based on input name

        if user_id is None:
            # creates new user id not in database
            add_user(connection, user_name)
            # re query for ID b/c auto increment
            user_id = get_user_id(connection, user_name)
            messagebox.showinfo("User Added", f"New user '{user_name}' has been added to the database.")
        
        if user_id:
            user_id = user_id[0]  # get u_id
            app = MealTrack(user_name, user_id)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Failed to get user ID")
            root.destroy()