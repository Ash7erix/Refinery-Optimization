import streamlit as st
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import json
import requests
import itertools as it
import matplotlib.pyplot as plt

# Load Data
with open("data.json", "r") as json_file:
    data = json.load(json_file)
data1 = list(data["distilYields"].values())
data2 = list(data["reformYields"].values())
data3 = list(data["crackingYields"].values())
rawMaterials = data["rawMaterials"]
finalProducts = data["finalProducts"]
productProfit = data["productProfit"]
distilOutputs = data["distilOutputs"]
reformOutputs = data["reformOutputs"]
crackingOutputs = data["crackingOutputs"]
distilYields = dict(zip(it.product(rawMaterials, distilOutputs), data1))
reformYields = dict(zip(it.product(distilOutputs[:3], reformOutputs), data2))
crackingYields = dict(zip(it.product(distilOutputs[3:5], crackingOutputs), data3))
used_in = data["used_in"]
used_to = [tuple(item) for item in data["used_to"]]
propor = data["propor"]
quality = data["quality"]
octane = data["octane"]
pressures = data["pressures"]
ingredient = data["ingredient"]
oils = data["distilOutputs"][3:5]
oils_plus = list(used_in.keys())[3:7]
naphthas = data["distilOutputs"][:3]
all_materials = rawMaterials + finalProducts + distilOutputs + reformOutputs + crackingOutputs
MaxCrudeOil1 = data["MaxCrudeOil1"]
MaxCrudeOil2 = data["MaxCrudeOil2"]
MinLubeOil = data["MinLubeOil"]
MaxLubeOil = data["MaxLubeOil"]

# Streamlit UI Setup
st.set_page_config(page_title="Refinery Optimization", page_icon="⛽", layout="wide")

st.markdown("""
    <style>
        .title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f4f4f9;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            color: #333;
        }
        .title-bar h1 {
            margin: 0;
            font-size: 49px;
            color: #333;
            margin-left: 20px;
        }
        .title-bar .logo1 {
            max-width: auto;
            height: 60px;
            margin-right: 20px;
        }
        .title-bar a {
            text-decoration: none;
            color: #0073e6;
            font-size: 16px;
        }
        .footer-text {
            font-size: 20px;
            background-color: #f4f4f9;
            text-align: left;
            color: #333;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
        }
    </style>
    <div class="title-bar">
        <h1>Problem 12.6 <br> Refinery Optimization</h1>
        <div>
            <a href="https://decisionopt.com" target="_blank">
                <img src="https://decisionopt.com/static/media/DecisionOptLogo.7023a4e646b230de9fb8ff2717782860.svg" class="logo1" alt="Logo"/>
            </a>
        </div>
    </div>
    <div class="footer-text">
    <p style="margin-left:20px;">  'Model Building in Mathematical Programming, Fifth Edition' by H. Paul Williams</p>
    </div>    
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
        .button {
            background-color: #FFFFFF;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        .button:hover {
            background-color: #FFFFFF;
             box-shadow: 1px 1px 4px rgb(255, 75, 75); /* Shadow effect on hover */
        }
    </style>
    <div class="container-c1">
        <br><p> For a detailed view of the mathematical formulation, please visit my 
        <a href="https://github.com/Ash7erix/Model_Building_Assignments/tree/main/12.6_Refinery_Optimization">Github</a> page.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
    </style>
    <div class="container-c1"> 
        <br><p>This app helps optimize Refinery Operations by determining the optimal allocation of raw materials, 
        refining processes, and product outputs to maximize profits while meeting operational constraints. It uses Gurobi 
        for Optimization, considering factors such as crude oil availability, refining capacities, product demands, and 
        quality specifications.</p>  
        <br><p>You can customize key parameters like crude oil limits and Lube Oil requirements using the 
        options on the left side. The app provides detailed insights, including the optimal quantities of refined 
        products, raw material usage, and profitability analysis, helping you make data-driven operational decisions.</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
    </style>
    <div class="container-c1">
        <br><p> You can view the mathematical formulation below by clicking the button.</p>
    </div>
""", unsafe_allow_html=True)
if st.button('Display Formulation'):
    def fetch_readme(repo_url):
        raw_url = f"{repo_url}/raw/main/12.6_Refinery_Optimization/README.md"  # Adjust path if necessary
        response = requests.get(raw_url)
        return response.text
    repo_url = "https://github.com/Ash7erix/Model_Building_Assignments"
    try:
        readme_content = fetch_readme(repo_url)
        st.markdown(readme_content)
        st.markdown("""---""")
    except Exception as e:
        st.error(f"Could not fetch README: {e}")
        st.markdown("""---""")


#SIDEBAR
st.sidebar.markdown(f"<h1><b>Optimization Parameters:</b></h1>",unsafe_allow_html=True)
MaxCrudeOil1 = st.sidebar.number_input("Max Crude Oil 1", min_value=0, value=MaxCrudeOil1)
MaxCrudeOil2 = st.sidebar.number_input("Max Crude Oil 2", min_value=0, value=MaxCrudeOil2)
MinLubeOil = st.sidebar.number_input("Min Lube Oil", min_value=0, value=MinLubeOil)
MaxLubeOil = st.sidebar.number_input("Max Lube Oil", min_value=0, value=MaxLubeOil)
max_distillation = st.sidebar.number_input("Max Distillation Capacity (barrels/day)", min_value=0, value=45000)
max_reforming = st.sidebar.number_input("Max Naphtha Reforming (barrels/day)", min_value=0, value=10000)
max_cracking = st.sidebar.number_input("Max Oil Cracking (barrels/day)", min_value=0, value=8000)


# Display Optimization Data in Tables
st.title("Optimization Data and Constraints:")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Final Products & Profits")
    final_products_df = pd.DataFrame.from_dict(productProfit, orient="index", columns=["Profit per Barrel ($)"])
    final_products_df.rename_axis("Product", inplace=True)
    st.dataframe(final_products_df)
with col2:
    st.subheader("Crude & Lube Oil Limits")
    limits_df = pd.DataFrame({
        "Constraint": ["Max Crude Oil 1", "Max Crude Oil 2", "Min Lube Oil", "Max Lube Oil"],
        "Value": [MaxCrudeOil1, MaxCrudeOil2, MinLubeOil, MaxLubeOil]})
    limits_df.index = range(1, len(limits_df) + 1)
    st.dataframe(limits_df)
with col3:
    st.subheader("Operational Constraints")
    constraints_df = pd.DataFrame({
        "Constraint": ["Max Distillation Capacity", "Max Naphtha Reforming", "Max Oil Cracking"],
        "Value": [max_distillation, max_reforming, max_cracking]})
    constraints_df.index = range(1, len(constraints_df) + 1)
    st.dataframe(constraints_df)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.subheader("Raw Materials")
    raw_materials_df = pd.DataFrame(rawMaterials, columns=["Raw Materials"])
    raw_materials_df.index = range(1, len(raw_materials_df) + 1)
    st.dataframe(raw_materials_df)
st.markdown("""---""")



# Optimization Model
model = gp.Model("Refinery Optimization")

x = model.addVars(all_materials, name="x")
y = model.addVars(used_to, name="y")
x["CrudeOil1"].ub = MaxCrudeOil1
x["CrudeOil2"].ub = MaxCrudeOil2
x["LubeOil"].ub = MaxLubeOil
x["LubeOil"].lb = MinLubeOil

# Objective: Maximize Profit
model.setObjective((gp.quicksum(productProfit[p] * x[p] for p in finalProducts)), GRB.MAXIMIZE)

# Constraints
model.addConstr((x["CrudeOil1"] + x["CrudeOil2"] <= 45000), name="distillation")
model.addConstr((gp.quicksum(y[n, "ReformedGasoline"] for n in naphthas) <= 10000), name="reforming")
model.addConstr((gp.quicksum(y[o, "Cracked"] for o in oils) <= 8000), name="cracking")

for p in distilOutputs:
    model.addConstr((x[p] == gp.quicksum(distilYields[m, p] * x[m] for m in rawMaterials)), name="dist" + p)

p = "ReformedGasoline"
model.addConstr((x[p] == gp.quicksum(reformYields[n, p] * y[n, p] for n in naphthas)), name="refo" + p)

for p in crackingOutputs:
    model.addConstr((x[p] == gp.quicksum(crackingYields[o, p] * y[o, "Cracked"] for o in oils)), name="cracked" + p)

p = "LubeOil"
model.addConstr((x[p] == 0.5 * y[("Residuum", p)]), name="lube")

for p in naphthas:
    model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

for p in oils_plus:
    model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p]) + propor[p] * x["FuelOil"]), name=p)

p = "CrackedGasoline"
model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

p = "ReformedGasoline"
model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

for p in ["PremiumPetrol", "RegularPetrol", "JetFuel"]:
    model.addConstr((x[p] == gp.quicksum(y[i, p] for i in ingredient[p])), name=p)

model.addConstr((x["PremiumPetrol"] >= 0.4 * x["RegularPetrol"]), name="40perc")

for p in ["PremiumPetrol", "RegularPetrol"]:
    model.addConstr((quality[p] * x[p] <= gp.quicksum(octane[i] * y[i, p] for i in ingredient[p])), name="octa_" + p)

p = "JetFuel"
model.addConstr((x[p] >= gp.quicksum(pressures[i] * y[i, p] for i in ingredient[p])), name="pres_" + p)


# SOLVE MODEL
st.markdown("""
    <style>
        .container-c2 p {
            font-size: 20px;
            margin-bottom: 20px;
        }
    </style>
    <div class="container-c2">
        <br><p>Click on the button below to solve the optimization problem.</p>
    </div>
""", unsafe_allow_html=True)
if st.button("Solve Optimization"):
    model.optimize()
    if model.status == GRB.OPTIMAL:
        profit = model.objVal
        st.markdown("""---""")
        st.markdown(f"<h3>Total Profit : <span style='color:rgba(255, 75, 75, 1)  ;'> <b>$ {profit:.2f}</b></span></h3>",unsafe_allow_html=True)
        st.markdown("""---""")
        results_df = pd.DataFrame([(p, x[p].x) for p in x.keys()], columns=["Material", "Quantity"])
        results_df = results_df[results_df["Quantity"] > 0]
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(results_df["Material"], results_df["Quantity"], color="#76b5c5")
        ax.set_xlabel("Material")
        ax.set_ylabel("Quantity (barrels/day)")
        ax.set_title("Refinery Output Quantities")
        plt.xticks(rotation=90, ha="right", fontsize=12)
        st.pyplot(fig)
        st.markdown("""---""")
        # Display Results
        st.markdown(f"<h3>Refinery Output:</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            results_df = results_df[results_df["Quantity"] > 0].sort_values(by="Quantity", ascending=False)
            results_df.index = range(1, len(results_df) + 1)
            st.dataframe(results_df[:8])
        with col2:
            results_df = results_df[results_df["Quantity"] > 0].sort_values(by="Quantity", ascending=False)
            results_df.index = range(1, len(results_df) + 1)
            st.dataframe(results_df[8:])

    else:
        st.error("No optimal solution found!")
    st.markdown("""
                                <style>
                                    footer {
                                        text-align: center;
                                        background-color: #f1f1f1;
                                        color: #333;
                                        font-size: 19px;
                                        margin-bottom:0px;
                                    }
                                    footer img {
                                        width: 44px; /* Adjust size of the logo */
                                        height: 44px;
                                    }
                                </style>
                                <footer>
                                    <h1>Author- Ashutosh <a href="https://www.linkedin.com/in/ashutoshpatel24x7/" target="_blank">
                                    <img src="https://decisionopt.com/static/media/LinkedIn.a6ad49e25c9a6b06030ba1b949fcd1f4.svg" class="img" alt="Logo"/></h1>
                                </footer>
                            """, unsafe_allow_html=True)
    st.markdown("""---""")
