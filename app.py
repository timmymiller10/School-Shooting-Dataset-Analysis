import pandas as pd
import dash
from dash import dcc
from dash import dash_table
from dash import html
import plotly.graph_objs as go

class MyApp:
    def __init__(self, incident, sum_killed, state_counts_df, shooter_t, mean_victims_situation_df, mean_victimskilled, situation_stats_df, mean_student_victim_age, 
                 mean_teacher_victim_age, mean_student_killed_age, mean_teacher_killed_age, male_percentage,female_percentage):
        self.data_load()
        self.incident = incident
        self.sum_killed = sum_killed
        self.state_counts_df = state_counts_df
        self.shooter_t = shooter_t
        self.mean_victims_situation_df = mean_victims_situation_df
        self.mean_victimskilled = mean_victimskilled
        self.situation_stats_df = situation_stats_df
        self.weapon_counts = weapon_counts
        self.mean_student_victim_age = mean_student_victim_age
        self.mean_teacher_victim_age = mean_teacher_victim_age
        self.mean_student_killed_age = mean_student_killed_age
        self.mean_teacher_killed_age = mean_teacher_killed_age
        self.male_percentage = male_percentage
        self.female_percentage = female_percentage
        self.app = dash.Dash(__name__, assets_folder='assets')
        self.set_layout()
    
    def data_load(self):
        user_input = input("Please enter the path to the Excel file: ")
        file = pd.read_excel(user_input)
        # Prompt the user for a file path
        all_sheets = file.sheet_names # gets list of all sheet names
        dfs = {sheet: file.parse(sheet) for sheet in all_sheets} # dictionary of dataframes for each sheet

        # seperate data into 4 sets
        incident = dfs['Incident']
        shooter = dfs['Shooter']
        victim = dfs['Victim']
        weapon = dfs['Weapon']

        count_by_year = incident['Year'].value_counts().reset_index()
        count_by_year.columns = ['Year', 'Total']

        # sums of victims killed for each year
        sum_killed = incident.groupby('Year')['Victims_Killed'].sum().reset_index()
        mean_victimskilled = incident.groupby('Year')['Victims_Killed'].sum().mean()
        max_victims_situation = incident.groupby('Situation')['Number_Victims'].max()
        min_victims_situation = incident.groupby('Situation')['Number_Victims'].min()
        min_max_victims_situation_df = pd.DataFrame({
            'Situation': min_victims_situation.index,
            'Min_Number_Victims': min_victims_situation.values,
            'Max_Number_Victims': max_victims_situation.values
        }).set_index('Situation')

        situation_stats_df = pd.merge(
            mean_victims_situation_df,
            min_max_victims_situation_df,
            on='Situation'
            )
        # state_counts_df
        # number of shootings in each state
        state_counts = incident['State'].value_counts()
        state_counts_fatal = fatal_incidents['State'].value_counts()
        # Convert the series to dataframes
        state_counts_df = state_counts.reset_index()
        state_counts_fatal_df = state_counts_fatal.reset_index()

        # Rename the columns
        state_counts_df.columns = ['State', 'Total School Shootings']
        state_counts_fatal_df.columns = ['State', 'Fatal School Shootings']

        # Merge the dataframes
        state_counts_df = pd.merge(state_counts_df, state_counts_fatal_df, on='State')

        state_counts_df['Fatal / Total'] = state_counts_df['Fatal School Shootings']/state_counts_df['Total School Shootings'] 
        # shooter_t
        # creating duplicate data to 'tidy'
        shooter_t = shooter

        # fill null vals in School_Affiliation with 'Unknown'
        shooter_t['School_Affiliation'].fillna('Unknown', inplace=True)

        # fill null in Race column with 'Other/Unknown'
        shooter_t['Race'].fillna('Other/Unknown', inplace=True)
        # replace 'Other' with 'Other/Unknown'
        shooter_t['Race'].replace('Other', 'Other/Unknown', inplace=True)

        # fill null in shooter outcome column with 'Unknown'
        shooter_t['Shooter_Outcome'].fillna('Unknown', inplace=True)

        # fill null in injury column with 'None'
        shooter_t['Injury'].fillna('None', inplace=True)

        shooter_t['Age'] = pd.to_numeric(shooter_t['Age'], errors='coerce')
        shooter_t.dropna(subset=['Age'], inplace=True)


        shooter_t.dropna(subset=['Age', 'Gender', 'Shooter_Died'], inplace=True) # drop observations with null values for age, gender, and if the shooter died
        # mean_victims_situation_df,
        # mean_victimskilled,
        # situation_stats_df,
        # mean_student_victim_age,
        # mean_teacher_victim_age,
        # mean_student_killed_age,
        # mean_teacher_killed_age,
        # male_percentage,
        # female_percentage

    def set_layout(self):
        self.app.layout = html.Div(children=[
            html.H1(children='School Shooting Data Analysis'),
            dcc.Tabs(id="tabs", value='tab-1', children=[
                dcc.Tab(label='Introduction', value='tab-0', children=[
                    html.Div([
                        html.H2('Introduction'),
                        html.P('This dashboard is designed to present an analysis on school shootings data. Here you can find a number of graphs and tables, each providing unique insights:'),
                        html.P('1. Age and Gender Statistics'),
                        html.P('2. "Counts by Year" tab: Shows the number of incidents per year.'),
                        html.P('3. "Victims Killed by Year" tab: Shows the number of victims killed per year.'),
                        html.P('4. "School Shootings by State" tab: Displays the total and fatal school shootings per state.'),
                        html.P('5. "Boxplot of Shooter\'s Age" tab: Provides a box plot of the shooter\'s age.'),
                        html.P('6. "Mean Victims Situation Table" tab: Gives a table of mean victims per situation.'),
                        html.P('7. "Weapon and Victims" tab: Shows the counts of victims for each weapon type.')
                    ])
                ]),
                
                dcc.Tab(label='Victim Statistics', value='tab-1', children=[
                    html.Div([
                    dcc.Graph(id='line_chart1', figure=self.create_line_chart_figure()),
                    html.H2('Age Statistics:'),
                    html.P('Average Age of all Student Victims: {}'.format(self.mean_student_victim_age)),
                    html.P('Average Age of Students Killed: {}'.format(self.mean_student_killed_age)),
                    html.P('Average Age of all Teacher Victims: {}'.format(self.mean_teacher_victim_age)),
                    html.P('Average Age of Teachers Killed: {}'.format(self.mean_teacher_killed_age)),
                    html.P('_____________________________________________________'),
                    html.H2('Gender Percentages:'),
                    html.P('Male: {:.2f}%'.format(self.male_percentage)),
                    html.P('Female: {:.2f}%'.format(self.female_percentage))]),
                    ]),
                
                dcc.Tab(label='Counts by Year', value='tab-2', children=[
                    dcc.Graph(id='graph1', figure=self.create_graph1_figure())
                ]),
                
                dcc.Tab(label='Victims Killed by Year', value='tab-3', children=[
                    dcc.Graph(id='line_chart', figure=self.create_line_chart_figure())
                ]),
                
                dcc.Tab(label='School Shootings by State', value='tab-4', children=[
                    dcc.Graph(id='graph2', figure=self.create_graph2_figure())
                ]),
                
                dcc.Tab(label="Boxplot of Shooter's Age", value='tab-5', children=[
                    html.Div([
                        dcc.Graph(id='box_plot', figure=self.create_box_plot_figure()),
                        html.P('Here we can see the age of all school shooters organized in a horizontal boxplot. The oldest school shooter was 78, while the youngest was a mere 7 years old. Most shooters are between 15-20 years old.')
                    ])
                ]),
                dcc.Tab(label='Mean Victims Situation Table', value='tab-6', children=[
                    html.Div(children=[
                        dash_table.DataTable(
                            id='table1',
                            columns=[{"name": i, "id": i} for i in self.mean_victims_situation_df.columns],
                            data=self.create_table().to_dict('records'),
                            style_data={
                                'backgroundColor': '#23282D',
                                'color': 'white'
                            },
                            style_header={
                                'backgroundColor': '#23282D',
                                'color': 'white'
                            },
                            style_table={
                                'backgroundColor': '#23282D',
                                'color': 'white',
                            }
                            
                        )
                    ], style={'width':'50%', 'display':'inline-block', 'fontFamily':'Arial, sans-serif'})
                ]),
                dcc.Tab(label='Weapon and Victims', value='tab-6', children=[
                    html.Div(children=[
                        dash_table.DataTable(
                            id='table2',
                            columns=[{"name": i, "id": i} for i in self.weapon_counts.columns],
                            data=self.weapon_counts.to_dict('records')
                        )
                    ], style={'width':'50%', 'display':'inline-block', 'fontFamily':'Arial, sans-serif'})
                ])
            ], style=dict(
                color='black',
                backgroundColor='#1C4E80')),
        ])


    def create_graph1_figure(self):
        count_by_year = self.incident.groupby('Year').size().reset_index(name='Counts')
        mean_count = count_by_year['Counts'].mean()

        return {
            'data': [
                go.Bar(
                    x=count_by_year['Year'],
                    y=count_by_year['Counts'],
                    name='Counts'
                ),
                go.Scatter(
                    x=count_by_year['Year'],
                    y=[mean_count]*len(count_by_year),
                    mode='lines',
                    name='Mean',
                    line=dict(
                        color='red',
                        dash='dash'
                    )
                )
            ],
            'layout': go.Layout(
                title='School Shootings by Year',
                yaxis={'title': 'Number of School Shootings'},
                plot_bgcolor='#23282D',
                paper_bgcolor='#23282D',
                font=dict(
                    color='#ffffff'
                )
                
            )
        }

    def create_line_chart_figure(self):
        return {
            'data': [
                go.Scatter(
                    x=self.sum_killed['Year'],
                    y=self.sum_killed['Victims_Killed'],
                    mode='lines+markers',  # This creates a line chart with markers
                    name='Victims Killed'
                ),
                go.Scatter(
                    x=self.sum_killed['Year'],
                    y=[self.mean_victimskilled]*len(self.sum_killed),
                    mode='lines',
                    name='Mean Victims Killed',
                    line=dict(
                        dash='dash'
                    )
                )
            ],
            'layout': go.Layout(
                title='Victims Killed by Year',
                xaxis={'title': 'Year'},
                yaxis={'title': 'Number of Victims Killed'},
                plot_bgcolor='#23282D',
                paper_bgcolor='#23282D',
                font=dict(
                    color='#ffffff'
                )
            )
        }

    def create_graph2_figure(self):
        return {
            'data': [
                go.Bar(
                    x=self.state_counts_df['State'],
                    y=self.state_counts_df['Total School Shootings'],
                    name='Total'
                ),
                go.Bar(
                    x=self.state_counts_df['State'],
                    y=self.state_counts_df['Fatal School Shootings'],
                    name='Fatal'
                )
            ],
            'layout': go.Layout(
                title='School Shootings by State',
                yaxis={'title': 'Total'},
                barmode='group',
                plot_bgcolor='#23282D',
                paper_bgcolor='#23282D',
                font=dict(
                    color='#ffffff'
                )
            )
        }

    def create_box_plot_figure(self):
        return {
            'data': [
                go.Box(
                    x=self.shooter_t['Age'],
                    name="Shooter's Age",
                    marker=dict(
                        color='red'
                    )
                )
            ],
            'layout': go.Layout(
                title="Boxplot of Shooter's Age",
                plot_bgcolor='#23282D',
                paper_bgcolor='#23282D',
                font=dict(
                    color='#ffffff'
                )
                
            )
        }

    def create_table(self):
        situation_stats_df['Number_Victims'] = situation_stats_df['Number_Victims'].round(2)
        return self.situation_stats_df

    def run(self, debug=False):
        self.app.run_server(debug=debug)

if __name__ == '__main__':
    # Assuming all the DataFrame variables and mean_victimskilled are defined earlier in your code.
    my_app = MyApp(incident, 
                   sum_killed, 
                   state_counts_df, 
                   shooter_t,
                   mean_victims_situation_df,
                   mean_victimskilled,
                   situation_stats_df,
                   mean_student_victim_age,
                   mean_teacher_victim_age,
                   mean_student_killed_age,
                   mean_teacher_killed_age,
                   male_percentage,
                   female_percentage
                   )
    
    
    
    my_app.run(debug=False)
