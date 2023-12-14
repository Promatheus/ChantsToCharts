import tkinter as tk
from tkinter import filedialog as fd
from io import open

import pandas as pd
import csv
import codecs
import Elojel

import Sessions


def button_correct():
    Sessions.judge_query(2)
    update_queries()


def button_almost():
    Sessions.judge_query(1)
    update_queries()


def button_wrong():
    Sessions.judge_query(0)
    update_queries()


def button_delete():
    comment_field = 'Deleted: '
    comments.set('Deleted: ')
    selection = listboxPlayers.curselection()
    for i in selection[::-1]:
        Sessions.delete_players(listboxPlayers.get(i))
        comment_field += (listboxPlayers.get(i) + " ")
    update_gui()
    comments.set(comment_field)


def button_input():
    filename = fd.askopenfilename(initialdir="/", title="Select a CSV File", filetypes=(("CSV Files", "*.csv"),))
    try:
        read_file(filename)
    except UnicodeDecodeError:
        comments.set("Input file should be an imported CSV from the survey")
    except FileNotFoundError:
        pass


def read_file(filename):
    new_player_names = []
    with open(filename, newline='', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(reader)
        for row in reader:
            if len(row) > 1:
                if not Sessions.player_exists(row[1]):
                    new_player_names.append(row[1])
                Sessions.create_session(row)
    update_gui()
    if len(new_player_names) == 0:
        comments.set('No new players')
    elif len(new_player_names) == 1:
        comments.set('New player:' + new_player_names[0])
    elif len(new_player_names) > 5:
        comments.set(str(len(new_player_names)) + ' new players')
    else:
        comments.set('New Players:' + ', '.join(new_player_names))


def button_evaluate():
    chosen_players = []
    selection = listboxPlayers.curselection()
    for i in selection[::-1]:
        chosen_players.append(listboxPlayers.get(i))
    if chosen_players:
        common_eras = Sessions.common_eras(chosen_players)
        if common_eras:
            evaluation = []
            try:
                for chosen_player in chosen_players:
                    file_name = chosen_player + " Evaluation.xlsx"
                    summary = Sessions.summary(chosen_player, common_eras)
                    if len(evaluation) == 0:
                        evaluation += [summary[0], [i + ' - ' + j for i, j in zip(summary[1], summary[4])]]
                    evaluation += [summary[3], summary[6]]
                    df = pd.DataFrame({'genre': summary[0], 'artist': summary[1], 'answer for artist': summary[2],
                                       'guessed artist': summary[3], 'title': summary[4], 'answer for title': summary[5],
                                       'guessed title': summary[6]})
                    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
                    df.to_excel(writer, sheet_name='Evaluation', index=False, header=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Evaluation']
                    fmt_header = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'top', 'fg_color': '#1F618D',
                                                      'font_color': '#FFFFFF', 'border_color': '#FFFFFF', 'border': 1})
                    fmt_prompts = workbook.add_format({'fg_color': '#D4E6F1'})
                    fmt_answers = workbook.add_format({'fg_color': '#A2D9CE'})
                    for col, value in enumerate(df.columns.values):
                        worksheet.write(0, col, value, fmt_header)
                    worksheet.set_column("A:A", 20, fmt_prompts)
                    worksheet.set_column("B:B", 20, fmt_prompts)
                    worksheet.set_column("C:C", 20, fmt_answers)
                    worksheet.conditional_format('D2:D1048576', {'type': '2_color_scale'})
                    worksheet.set_column("E:E", 20, fmt_prompts)
                    worksheet.set_column("F:F", 20, fmt_answers)
                    worksheet.conditional_format('G2:G1048576', {'type': '2_color_scale'})
                    writer.save()
                df = pd.DataFrame({'genre': evaluation[0], 'track': evaluation[1]})
                for num, player in enumerate(chosen_players):
                    df[player + ' a.score'] = evaluation[2 + num*2]
                    df[player + ' t.score'] = evaluation[3 + num*2]
                maximum_guesses = len(chosen_players) * 2 + 2
                for i, row in df.iterrows():
                    artist_score = 10*(maximum_guesses/(sum(row[2:maximum_guesses - 1:2]) + 2))
                    df.iloc[i, 2:maximum_guesses - 1:2] *= int(artist_score / 2)
                    title_score = 10*(maximum_guesses/(sum(row[3:maximum_guesses:2]) + 2))
                    df.iloc[i, 3:maximum_guesses:2] *= int(title_score / 2)
                df2 = df.groupby(['genre'], as_index=False).sum()
                for num, player in enumerate(chosen_players):
                    df2[player + ' a.score'] = df2[player + ' a.score'] + df2[player + ' t.score']
                    df2.rename(columns={player + ' a.score': player + ' score'}, inplace=True)
                    df2.drop(player + ' t.score', inplace=True, axis=1)
                writer = pd.ExcelWriter('KS_Evaluation.xlsx', engine='xlsxwriter')
                df.to_excel(writer, sheet_name='KS_Evaluation', index=False)
                df2.to_excel(writer, sheet_name='Genre Winners', index=False)
                workbook = writer.book
                worksheet = writer.sheets['KS_Evaluation']
                worksheet2 = writer.sheets['Genre Winners']
                fmt_header = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'top', 'fg_color': '#1F618D',
                                                  'font_color': '#FFFFFF', 'border_color': '#FFFFFF', 'border': 1})
                for col, value in enumerate(df.columns.values):
                    worksheet.write(0, col, value, fmt_header)
                for col, value in enumerate(df2.columns.values):
                    worksheet2.write(0, col, value, fmt_header)
                worksheet2.set_column("A:A", 20)
                writer.save()
                comment_string = "Evaluated with these common eras: " + ",".join([str(era) for era in common_eras])
                comments.set(comment_string)
            except PermissionError:
                comments.set("The target files are not accessible")
        else:
            comments.set("At least one survey has to be filled by all players")
    else:
        comments.set("Choose which players to evaluate")


def update_gui():
    listboxPlayers.delete(0, tk.END)
    for player in Sessions.players():
        listboxPlayers.insert(0, player)
    update_queries()


def update_queries():
    prompt_query = Sessions.prompt_query()
    if prompt_query:
        prompt.set(prompt_query[0])
        answer.set(prompt_query[1])
        comments.set(str(Sessions.count_queries()) + " queries left")
    else:
        prompt.set('')
        answer.set('')
        comments.set("No queries")


def load_sessions():
    Sessions.sessions.clear()
    with open('session_data.csv', newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            try:
                Sessions.load_session(row)
            except IndexError:
                pass
    update_gui()


def button_save():
    with codecs.open('session_data.csv', mode='w', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for session in Sessions.sessions:
            writer.writerow(session.as_row())
    comments.set("Sessions saved")


if __name__ == '__main__':
    window = tk.Tk()
    window.geometry("400x300+384+168")
    window.minsize(400, 300)
    window.title("Kottától a Spotify-ig Kiértékelő")
    window.configure(background="#6082B6")
    window.iconbitmap("KS_Icon.ico")

    listboxPlayers = tk.Listbox(
        background="#A7C7E7",
        font="TkFixedFont",
        selectmode='multiple',
        foreground="#000000",
        selectbackground="blue",
        selectforeground="white")
    listboxPlayers.place(relx=0.025, rely=0.05, relheight=0.875, relwidth=0.3)

    buttonCorrect = tk.Button(
        background="#7CFC00",
        activebackground="#228B22",
        font="-family {Segoe UI} -size 12",
        text='Correct',
        command=button_correct)
    buttonCorrect.place(relx=0.35, rely=0.35, height=32, width=60)

    buttonAlmost = tk.Button(
        background="#F8DE7E",
        activebackground="#DAA520",
        font="-family {Segoe UI} -size 12",
        text='Almost',
        command=button_almost)
    buttonAlmost.place(relx=0.56, rely=0.35, height=32, width=60)

    buttonWrong = tk.Button(
        background="#EE4B2B",
        activebackground="#A52A2A",
        font="-family {Segoe UI} -size 12",
        text='Wrong',
        command=button_wrong)
    buttonWrong.place(relx=0.77, rely=0.35, height=32, width=60)

    buttonDelete = tk.Button(
        background="#A9A9A9",
        activebackground="#71797E",
        foreground="#ffffff",
        activeforeground="#ffffff",
        font="-family {Segoe UI} -size 12",
        text='Delete',
        command=button_delete)
    buttonDelete.place(relx=0.35, rely=0.50, height=32, width=60)

    buttonInput = tk.Button(
        background="#A9A9A9",
        activebackground="#71797E",
        foreground="#ffffff",
        activeforeground="#ffffff",
        font="-family {Segoe UI} -size 12",
        text='Input',
        command=button_input)
    buttonInput.place(relx=0.56, rely=0.50, height=32, width=60)

    buttonSave = tk.Button(
        background="#A9A9A9",
        activebackground="#71797E",
        foreground="#ffffff",
        activeforeground="#ffffff",
        font="-family {Segoe UI} -size 12",
        text='Save',
        command=button_save)
    buttonSave.place(relx=0.77, rely=0.50, height=32, width=60)

    buttonEvaluate = tk.Button(
        background="#A9A9A9",
        activebackground="#71797E",
        foreground="#ffffff",
        activeforeground="#ffffff",
        font="-family {Segoe UI} -size 12",
        text='Evaluate selected players',
        command=button_evaluate)
    buttonEvaluate.place(relx=0.35, rely=0.65, height=32, width=200)

    prompt = tk.StringVar()
    labelPrompt = tk.Label(
        anchor='w',
        background="#6082B6",
        font="-family {Segoe UI} -size 12",
        foreground="#ffffff",
        relief="ridge",
        textvariable=prompt)
    labelPrompt.place(relx=0.35, rely=0.05, height=32, relwidth=0.63)

    answer = tk.StringVar()
    labelAnswer = tk.Label(
        anchor='w',
        background="#6082B6",
        font="-family {Segoe UI} -size 12",
        foreground="#ffffff",
        relief="ridge",
        textvariable=answer)
    labelAnswer.place(relx=0.35, rely=0.20, height=32, relwidth=0.63)

    comments = tk.StringVar()
    labelComments = tk.Label(
        anchor='w',
        background="#6082B6",
        font="-family {Segoe UI} -size 12",
        textvariable=comments)
    labelComments.place(relx=0.025, rely=0.885, height=32, relwidth=0.95)

    try:
        load_sessions()
    except FileNotFoundError:
        pass
    update_queries()
    window.mainloop()
