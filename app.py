from flask import Flask, render_template, request, redirect,send_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
import os
matplotlib.use('Agg')

app = Flask(__name__)

output_dir = 'output_files'
os.makedirs(output_dir, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # Perform modification on the CSV file
    df = pd.read_excel(file)

    # Create a pivot table using effort
    pivot_table = pd.pivot_table(df, index='E. No', values='effort', aggfunc='sum')
    pivot_table = pivot_table.sort_values (by='effort', ascending=True)

    # Store the pivot table in Excel sheet
    pivot_table.to_excel('pivot.xlsx')
    print(pivot_table)

    # Calculate the median for the effort values
    median_effort = pivot_table['effort'].median()
    print(f"Median Effort: {median_effort}")

    # Filter employees based on effort
    selected_eno_df = df[df['E. No'].isin(pivot_table[pivot_table['effort'] <= median_effort].index)]
    new_pivot_table = pd.pivot_table(selected_eno_df, index='E. No', columns='Month', values='effort', aggfunc='sum')

    # Replace column names and NaN values
    col_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    new_pivot_table.columns = col_names
    new_pivot_table = new_pivot_table.fillna(0)
    pd.options.display.float_format = '{:.0f}'.format

    # Store the pivot table in Excel sheet
    new_pivot_table.to_excel('effort.xlsx')
    print(new_pivot_table)

    # Save the modified DataFrame to a new Excel file
    output_filename = 'modified_salary.xlsx'
    new_pivot_table.to_excel(output_filename, index=False)

    # ... (generate the bar chart)
    df=df[df['E. No']!='GUEST']
    employee_numbers = df['E. No']
    employee_productivity = df['PRODUCTIVITY']
    employee_effort = df['effort']
    x = np.arange(len(employee_numbers))

    # Define the width of the bars (optional)
    bar_width = 0.20
    plt.figure(figsize=(15, 6)) 

    # Create a bar graph for productivity 
    plt.bar(x - bar_width/2, employee_productivity, bar_width, label='Productivity', align='center')
  

    # Set the x-axis labels
    step = 4
    plt.xticks(x[::step], employee_numbers[::step], rotation=0)
    plt.ylim(0, 200) 
    plt.xlim(0, 200) 
    # Add labels and a title
    plt.xlabel('Employee Number')
    plt.ylabel('Percentage')
    plt.title('Employee Productivity ')

    # Add a legend
    plt.legend()

    # Save the plot as an image in memory
    image = BytesIO()
    plt.savefig(image, format="png")
    image.seek(0)
    image_base64 = base64.b64encode(image.read()).decode()

    effort_by_code = df.groupby('E. Code')['effort'].sum()

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(effort_by_code, labels=effort_by_code.index, autopct='%1.1f%%')
    plt.title('Effort Distribution by E. Code')

    # Save the pie chart as an image in memory
    pie_image = BytesIO()
    plt.savefig(pie_image, format="png")
    pie_image.seek(0)
    pie_image_base64 = base64.b64encode(pie_image.read()).decode()

    # Create an HTML table from the pivot table
    pivot_table_html = new_pivot_table.to_html(classes='table table-bordered', escape=False)
    pivot_table2_html = pivot_table.to_html(classes='table table-bordered', escape=False)
    # Render the HTML template with the base64 image and pivot table
    return render_template('graph.html',pie_image_base64=pie_image_base64, image_base64=image_base64,median_effort=median_effort,pivot_table2=pivot_table2_html,pivot_table=pivot_table_html)

if __name__ == '__main__':
    app.run(debug=True)
