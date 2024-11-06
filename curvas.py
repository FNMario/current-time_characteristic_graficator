import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from clases import *


def get_url() -> str:
    """
    Reads the url from a text file and extracts the gid from the url.
    Returns the url in the format of 'https://docs.google.com/spreadsheets/d/.../export?gid=...&format=csv'
    """
    with open("google_sheets_name.txt", "r") as f:
        file = f.read()

    url_raw = file.strip()
    url_1, url_2 = url_raw.split('?')
    url_1 = '/'.join(url_1.split('/')[:-1])
    url_2 = url_2[url_2.find('gid=') + 4:]
    end_1 = url_2.find('#')
    if end_1 != -1:
        url_2 = url_2[:end_1]
    end_2 = url_2.find('&')
    if end_2 != -1:
        url_2 = url_2[:end_2]
    url = url_1 + '/export?gid=' + url_2 + '&format=csv'

    return url


def get_data(url) -> pd.DataFrame:
    """
    Download the file and read it into a pandas DataFrame

    Returns
    -------
    pd.DataFrame
    """

    df = pd.read_csv(url,
                     index_col=0,
                     skiprows=2,
                     )
    df = df.iloc[:, :27]
    df.columns = ['sector', 'carga', 'es_emergencia', 'nombre', 'I_n', 'cond_nombre',
                  'borrar_1', 'cond_S', 'cond_I_adm', 'cond_K', 'borrar_2', 'term_nombre', 'term_I_t', 'term_I_cc',
                  'term_I_r', 'term_t_r', 'term_I_sd', 'term_t_sd', 'term_I_i',
                  'term_curva', 'gm_nombre', 'gm_I_t', 'gm_I_cc', 'gm_curva', 'fus_nombre', 'fus_I_f',
                  'alimentador']
    df.drop(['borrar_1', 'borrar_2'], axis=1, inplace=True)

    df.reset_index(drop=True, inplace=True)
    df.drop([0], axis=0, inplace=True)

    # Clean columns

    df["es_carga"] = df["carga"].notna()
    df["es_emergencia"] = df["es_emergencia"] == "SI"

    def seccion(s):
        if not type(s) == str:
            return s
        s = s.replace(",", ".")
        if '/' in s:
            s = s.split('/')[0]
        if 'x' in s:
            s = np.prod([float(x) for x in s.split('x')])
        return float(s)

    df["cond_S"] = df["cond_S"].apply(seccion)

    num_cols = ["I_n", "cond_S", "cond_I_adm", "cond_K",
                'term_I_r', 'term_t_r', 'term_I_sd', 'term_t_sd', 'term_I_i',
                "term_I_t", "term_I_cc", "gm_I_t", "gm_I_cc", "fus_I_f"]
    for col in num_cols:
        df[col] = df[col].apply(lambda x: x.replace(
            ',', '.').strip() if type(x) == str else x).astype(float)

    return df


def create_tree(df: pd.DataFrame) -> dict:
    """
    Constructs a hierarchical tree structure based on the provided DataFrame.

    Iterates over each row in the DataFrame to create instances of Termica, 
    Proteccion, Conductor, Carga, or Barra, and connects them into a tree 
    structure. The function returns a dictionary mapping item names to their 
    corresponding leaf nodes within the tree.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing electrical network data with columns such as 
        'term_curva', 'term_nombre', 'term_I_t', 'term_I_cc', 'gm_nombre', 
        'fus_nombre', 'fus_I_f', 'cond_nombre', 'cond_S', 'cond_I_adm', 
        'cond_K', 'I_n', 'es_carga', and 'alimentador'.

    Returns
    -------
    dict
        A dictionary mapping item names from the DataFrame to their 
        corresponding leaf nodes in the constructed tree.
    """

    # Create a dictionary to store the items in the tree
    items = {}
    red = Red()
    for i, row in df.iterrows():
        if row["term_curva"] == 'C' and not pd.isna(row["term_nombre"]):
            termica = Termica(name=row["term_nombre"], I_t=row["term_I_t"],
                              I_cc=row["term_I_cc"], curva='C')
        elif row["term_curva"] == 'M' and not pd.isna(row["term_nombre"]):
            termica = Termica(name=row["term_nombre"], I_t=row["term_I_t"],
                              I_r=row["term_I_r"], t_r=row["term_t_r"],
                              I_sd=row["term_I_sd"], t_sd=row["term_t_sd"],
                              I_i=row["term_I_i"], I_cc=row["term_I_cc"], curva='M')
        elif not pd.isna(row["gm_nombre"]):
            termica = Termica(name=row["gm_nombre"], I_t=row["I_n"],
                              I_cc=row["gm_I_cc"], curva=row["gm_curva"])
        else:
            termica = None

        protecction = Proteccion(
            fusible=Fusible(name=row["fus_nombre"], I_f=row["fus_I_f"]) if not pd.isna(
                row["fus_I_f"]) else None,
            termica=termica)
        cable = Conductor(name=row["cond_nombre"], S=row["cond_S"],
                          I_adm=row["cond_I_adm"], K=row["cond_K"],
                          I_n=row["I_n"])
        if row["es_carga"]:
            leaf = Carga(name=row["nombre"], I_n=row["I_n"])
        else:
            leaf = Barra(name=row["nombre"])
        protecction.add_child(cable)
        cable.add_child(leaf)
        items.update({row["nombre"]: leaf})

    # associate each item with its parent

    for i, row in df.iterrows():
        child = items[row["nombre"]]
        while not isinstance(child, Proteccion):
            child = child.parent
        protecction = child

        if row["alimentador"] not in [None, np.nan]:
            items[row["alimentador"]].add_child(protecction)
        else:
            red.add_child(protecction)

    return items


def create_all_plots(df: pd.DataFrame, items: dict):
    """
    Creates a plot for each item in the items dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the data of the items.
    items : dict
        Dictionary with the items to plot.

    Notes
    -----
    The method creates a folder called "curvas" in the current directory, and
    stores the plots in there.

    The method sorts the DataFrame by index, and then iterates over it. For each
    row, it creates a plot using the create_plot method of the item, and saves it
    as a PNG file in the "curvas" folder.

    If an exception occurs while creating a plot, it is printed to the console.
    """

    # create folder to store the plots
    if not os.path.exists("./curvas"):
        os.mkdir("./curvas")

    # plot the curves
    df.sort_index(inplace=True)
    length = df.shape[0]
    for i, row in df.iterrows():
        try:
            fig = items[row["nombre"]].create_plot()
            fig.get_figure().savefig(
                f"./curvas/current-time_characteristic_{row['nombre']}.png", bbox_inches='tight')
            print(f"fig {i}/{length} - {row['nombre']} - {i*100/length:.1f}%")
            plt.close(fig)
        except Exception as e:
            print(e)


def create_plot(items: dict, name: str):
    """
    Creates a plot for the item with the given name.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the data of the items.
    items : dict
        Dictionary with the items to plot.
    name : str
        Name of the item to plot.

    Returns
    -------
    None
    """

    # create folder to store the plots
    if not os.path.exists("./curvas"):
        os.mkdir("./curvas")

    # plot the curve
    try:
        fig = items[name].create_plot()
        fig.get_figure().savefig(
            f"./curvas/current-time_characteristic_{name}.png", bbox_inches='tight')
        fig.show()
        input("Presione enter para continuar...")
        plt.close(fig)
    except Exception as e:
        print(e)


def run():
    print('Cargando datos...')
    url = get_url()
    df = get_data(url)
    items = create_tree(df)
    while True:
        response = input("""MENU
                        1. Crear todas las graficas
                        2. Crear una grafica
                        3. refrescar datos
                        9. Salir""")
        if response == 1:
            create_all_plots(df, items)
        elif response == 2:
            name = input(
                "Nombre de la barra/carga a graficar: ")
            if name == '':
                return
            if name not in items:
                print("La barra/carga no existe")
            else:
                create_plot(items, name)
        elif response == 3:
            print('Cargando datos...')
            df = get_data(url)
            items = create_tree(df)
        elif response == 9:
            return
        else:
            print("Respuesta invalida")


if __name__ == "__main__":
    run()
