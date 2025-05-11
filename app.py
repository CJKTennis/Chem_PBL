import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pubchempy as pcp
import wikipedia

# Set page config
st.set_page_config(page_title="Chemical Reaction Simulator", page_icon="⚗️")

# --- Chemical Simulator Class ---
class ChemicalReactionSimulator:
    def __init__(self):
        self.reactions = []
        self.reaction_df = pd.DataFrame()

    def predict_products(self, reactants):
        rules = {
            "H2 + O2": "H2O",
            "N2 + H2": "NH3",
            "C + O2": "CO2",
            "Na + Cl2": "NaCl",
            "Fe + O2": "Fe2O3"
        }
        return rules.get(reactants, "Unknown")

    def add_reaction(self, reactants, temperature, pressure, catalyst):
        products = self.predict_products(reactants)
        catalyst = catalyst if catalyst else "None"
        reaction = {
            "Reactants": reactants,
            "Products": products,
            "Temperature (°C)": temperature,
            "Pressure (atm)": pressure,
            "Catalyst": catalyst
        }
        self.reactions.append(reaction)

    def simulate_reactions(self):
        data = {
            "Reactants": [],
            "Products": [],
            "Temperature (°C)": [],
            "Pressure (atm)": [],
            "Catalyst": [],
            "Reaction Rate (mol/s)": [],
            "Yield (%)": []
        }
        for reaction in self.reactions:
            temp = reaction["Temperature (°C)"]
            pressure = reaction["Pressure (atm)"]
            has_catalyst = reaction["Catalyst"] != "None"
            rate = round((temp * 0.05 + pressure * 0.3) * (1.2 if has_catalyst else 1.0), 2)
            yield_percent = round(min(100, temp * 0.2 + pressure * 1.5 + (10 if has_catalyst else 0)), 2)
            for key in reaction:
                data[key].append(reaction[key])
            data["Reaction Rate (mol/s)"].append(rate)
            data["Yield (%)"].append(yield_percent)
        self.reaction_df = pd.DataFrame(data)

    def get_product_info(self, product_name):
        try:
            compounds = pcp.get_compounds(product_name, 'name')
            if not compounds:
                return {"Error": "Compound not found."}
            c = compounds[0]
            return {
                "IUPAC Name": c.iupac_name,
                "Molecular Formula": c.molecular_formula,
                "Molecular Weight": c.molecular_weight,
                "Canonical SMILES": c.canonical_smiles,
                "Is Likely a Solvent?": "Yes" if "solvent" in str(c.synonyms).lower() else "Possibly No",
                "Synonyms": c.synonyms[:5] if c.synonyms else []
            }
        except Exception as e:
            return {"Error": str(e)}

    def get_wikipedia_summary(self, chemical):
        try:
            return wikipedia.summary(chemical, sentences=2)
        except:
            return "No Wikipedia summary found."

    def plot_reactions(self):
        if self.reaction_df.empty:
            st.warning("No reactions to plot.")
            return

        fig, ax = plt.subplots(1, 2, figsize=(14, 5))

        ax[0].bar(self.reaction_df["Reactants"], self.reaction_df["Reaction Rate (mol/s)"])
        ax[0].set_title("Reaction Rates")
        ax[0].set_ylabel("mol/s")
        ax[0].tick_params(axis='x', rotation=45)

        ax[1].bar(self.reaction_df["Reactants"], self.reaction_df["Yield (%)"])
        ax[1].set_title("Reaction Yields")
        ax[1].set_ylabel("% Yield")
        ax[1].tick_params(axis='x', rotation=45)

        st.pyplot(fig)

# --- App Logic ---
simulator = ChemicalReactionSimulator()

st.title("⚗️ Chemical Reaction Simulator")

st.sidebar.header("Input Reaction Parameters")
reactants = st.sidebar.text_input("Reactants (e.g., H2 + O2)")
temperature = st.sidebar.number_input("Temperature (°C)", value=25.0)
pressure = st.sidebar.number_input("Pressure (atm)", value=1.0)
catalyst = st.sidebar.text_input("Catalyst (optional)")

valid_input = True
if temperature < -273.15:
    st.sidebar.error("Temperature must be above absolute zero.")
    valid_input = False
if pressure < 0:
    st.sidebar.error("Pressure must be non-negative.")
    valid_input = False

if st.sidebar.button("Add Reaction"):
    if reactants and valid_input:
        simulator.add_reaction(reactants, temperature, pressure, catalyst)
        simulator.simulate_reactions()
        st.success("Reaction added and simulated.")
    elif not reactants:
        st.warning("Please enter reactants.")

if simulator.reaction_df.empty:
    st.info("Add a reaction using the sidebar to see results.")
else:
    st.subheader("🧪 Reaction Predictions Table")
    st.dataframe(simulator.reaction_df)

    st.download_button("📥 Download Results as CSV",
                       simulator.reaction_df.to_csv(index=False).encode('utf-8'),
                       "reactions.csv", "text/csv")

    st.subheader("📊 Reaction Visualizations")
    simulator.plot_reactions()

    # Product Info Section
    st.subheader("🔍 Chemical Product Lookup")
    selected_product = st.selectbox("Select a product to learn more", simulator.reaction_df["Products"].unique())

    with st.expander(f"ℹ️ Details for {selected_product}"):
        pubchem_info = simulator.get_product_info(selected_product)
        wiki_summary = simulator.get_wikipedia_summary(selected_product)

        st.markdown("**PubChem Data:**")
        st.json(pubchem_info)

        st.markdown("**Wikipedia Summary:**")
        st.info(wiki_summary)
