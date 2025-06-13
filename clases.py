from dataclasses import dataclass, field
from typing import Optional

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
# Se crea un estructura de arbol que representa un diagrama electrico unifilar
# Primero se crea la clase nodo


def round_to_text(number):
    if number % 1 < 1e-2:
        return f"{number:.0f}"
    else:
        return f"{number}"


def lighten_color(color, amount=-0.5):
    """
    Lightens or darkens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    amount = amount / 2.0 + 0.5  # Scale amount to range 0 to 1
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


@dataclass
class Nodo:
    name: str
    parent: Optional['Nodo'] = None

    def add_plot(self, *args, **kwargs):
        if self.parent is None:
            raise ValueError(f"El nodo {self.name} no tiene padre")
        if isinstance(self, Conductor):
            new_color = self.new_color()
            kwargs.update(color=new_color)
        self.parent.add_plot(*args, **kwargs)
        self.plot(*args, **kwargs)

    def plot(self, *args, **kwargs):
        pass

    def add_child(self, child: Optional['Nodo']):
        if hasattr(self, "children"):
            self.children.append(child)
            child.parent = self
        elif hasattr(self, "child"):
            self.child = child
            child.parent = self

    def get_children(self):
        if hasattr(self, "children"):
            return self.children
        elif hasattr(self, "child"):
            return [self.child]

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        def print_tree(node: Nodo, text: str, level=0):
            if node is None:
                return ""
            if isinstance(node, (Carga, Barra)):
                text = text + f"    {'┃   ' * level}┣━ {node.name}\n"
                level += 1
            children = node.get_children()
            if children is None:
                return text
            for child in children:
                text = print_tree(child, text, level)
            return text

        parents = list()
        child = self
        while not isinstance(child, Red):
            child = child.parent
            if isinstance(child, (Carga, Barra)):
                parents.append(child)
        red = child

        text = ""
        tabs = len(parents)

        # Add parents to list
        for tab, item in enumerate(parents):
            text = f"    {'┃   ' *(tabs-tab-1)}┣━ {item.name}\n" + text

        text = f"=={red.name}\n" + text

        text = print_tree(self, text, tabs)

        return text


@dataclass
class GraphicCreator():

    def create_plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
        self.add_plot(ax=ax)
        # ax.set_aspect(0.707)
        conductores = [
            line for line in ax.lines if line.get_linestyle() == '-']
        x_min = ax.get_xlim()[0]
        pot_x_min = int(np.floor(np.log10(x_min)))
        x_max = max([max(line.get_xdata()) for line in conductores])
        pot_x_max = int(np.round(np.log10(x_max)))
        ax.set_xticks(
            list(np.logspace(pot_x_min, pot_x_max, pot_x_max - pot_x_min + 1)))
        ax.set_xlim(x_min, x_max)
        ax.set_yticks(list(np.logspace(-3, 6, 10)))
        ax.set_ylim([0.001, 1000000])
        ax.grid(True, which='both')
        ax.legend(loc='upper right')
        ax.set_xlabel('Intensidad (A)')
        ax.set_ylabel('Tiempo (s)')
        ax.set_title(
            f"Curvas para {self.name}" if self.name else 'Curva Intensidad tiempo')
        return fig


# Ahora se crean las clases que heredan de la clase nodo, y representan las partes de un sistema electrico: Red, Barras, Protecciones y Cargas

@dataclass
class Red(Nodo):
    name: str = field(default="red")
    parent: Nodo = field(default=None)
    child: Nodo = None

    def add_plot(self, *args, **kwargs):
        return


@dataclass
class Fusible():
    I_f: float
    name: str = field(default="fusible")

    def plot(self, color: str, ax: plt.Axes, *args, **kwargs):
        tiempo_1 = [0.001, 0.01862087136662867, 0.04875284901033861, 0.09999999999999998, 0.4875284901033862, 1.0, 4.875284901033865,
                    10.000000000000002, 48.752849010338664, 100.00000000000004, 487.5284901033861, 1000.0000000000007, 1148.1536214968828]
        tiempo_2 = [0.001, 0.01862087136662867, 0.04875284901033861, 0.09999999999999998, 0.4875284901033862, 1.0, 4.875284901033865,
                    10.000000000000002, 48.752849010338664, 100.00000000000004, 487.5284901033861, 1000.0000000000007, 3311.3112148259115]
        tiempo_3 = [0.001, 0.01862087136662867, 0.04875284901033861, 0.09999999999999998, 0.4875284901033862, 1.0, 4.875284901033865,
                    10.000000000000002, 48.752849010338664, 100.00000000000004, 487.5284901033861, 1000.0000000000007, 3981.07170553497]
        fusibles = {
            6: {'t': tiempo_1, 'I': [239.88329190194912, 88.71560120379613, 68.07693586937418, 56.36376558259544, 38.72576449216175, 33.11311214825913, 23.442288153199236, 20.55890595984142, 15.776112696993486, 14.387985782558454, 12.302687708123818, 11.534532578210925, 11.428783347897722]},
            10: {'t': tiempo_1, 'I': [354.81338923357566, 139.31568029453047, 104.47202192208005, 86.09937521846008, 57.94286964268813, 49.20395356814511, 35.07518739525681, 30.76096814740709, 23.988329190194907, 22.387211385683404, 19.952623149688804, 19.142559250210862, 19.054607179632477]},
            16: {'t': tiempo_1, 'I': [512.8613839913652, 199.52623149688802, 153.46169827992946, 125.31411749414158, 82.03515443298187, 69.18309709189366, 49.317380395493615, 43.05266104917107, 34.119291162192866, 31.1171633710602, 27.227013080779138, 25.82260190634596, 25.585858869056462]},
            20: {'t': tiempo_1, 'I': [724.4359600749902, 316.22776601683825, 245.4708915685033, 199.06733389871874, 130.0169578033291, 107.15193052376065, 75.33555637337177, 65.01296903430907, 48.194779762512745, 43.55118736855688, 34.994516702835746, 32.433961734934925, 32.13660538640317]},
            25: {'t': tiempo_1, 'I': [891.2509381337466, 398.1071705534976, 300.6076302628233, 242.66100950824162, 162.55487557504838, 136.45831365889245, 92.04495717531714, 79.79946872679767, 60.39486293763802, 53.333489548762124, 43.85306977749857, 40.83193863326923, 40.17908108489401]},
            32: {'t': tiempo_1, 'I': [1122.0184543019636, 475.33522594280566, 358.9219346450057, 295.8012466551549, 198.15270258050998, 165.95869074375622, 117.21953655481305, 103.0386120441616, 77.62471166286922, 69.18309709189366, 54.32503314924336, 51.522864458175654, 51.522864458175654]},
            40: {'t': tiempo_1, 'I': [1412.5375446227545, 630.9573444801932, 496.59232145033644, 411.14972110452226, 271.01916318908434, 229.08676527677744, 162.92960326397235, 142.232878712282, 105.9253725177289, 93.54056741475524, 70.95777679633893, 65.01296903430907, 64.12095765851618]},
            50: {'t': tiempo_1, 'I': [1995.2623149688804, 851.1380382023776, 636.7955209079158, 526.0172663907065, 345.9393778261222, 291.7427014001168, 207.96966871036966, 181.55156627731353, 133.04544179780916, 117.48975549395293, 88.92011178579486, 81.84647881347904, 80.16780633876796]},
            63: {'t': tiempo_1, 'I': [2630.2679918953822, 1091.4403364487573, 866.9618757582173, 707.9457843841387, 453.94161665020357, 376.7037989839092, 259.4179362118817, 228.034207200042, 169.82436524617444, 151.3561248436209, 115.34532578210927, 103.2761405761397, 101.39113857366796]},
            80: {'t': tiempo_2, 'I': [3548.133892335754, 1592.2087270511718, 1282.3305826560227, 1083.9269140212048, 711.213513653329, 586.1381645140291, 403.64539296760523, 348.3373150360119, 247.74220576332866, 216.2718523727022, 157.03628043335542, 141.57937799570811, 124.16523075924107]},
            100: {'t': tiempo_2, 'I': [4466.835921509634, 1995.2623149688804, 1603.2453906900423, 1348.962882591654, 887.1560120379614, 734.5138681571156, 506.9907082747048, 434.51022417157156, 311.17163371060195, 268.5344445658508, 196.3360276836048, 177.0108958317423, 154.8816618912482]},
            125: {'t': tiempo_2, 'I': [5623.413251903499, 2511.886431509581, 2018.3663636815636, 1690.4409316432666, 1106.6237839776668, 918.3325964835813, 628.0583588133181, 542.0008904016242, 398.1071705534976, 348.3373150360119, 258.82129151530927, 227.5097430772073, 195.43394557753948]},
            160: {'t': tiempo_2, 'I': [7079.457843841383, 3349.654391578277, 2685.344445658508, 2238.7211385683418, 1482.5180851459545, 1230.2687708123824, 833.6811846196346, 724.4359600749902, 533.3348954876211, 467.7351412871983, 346.7368504525318, 304.78949896279846, 247.17241450161296]},
            200: {'t': tiempo_2, 'I': [9120.108393559109, 4466.835921509634, 3589.219346450058, 2999.1625189876513, 1954.3394557753952, 1629.296032639724, 1101.539309541415, 939.7233105646382, 688.6522963442766, 601.1737374832782, 443.6086439314326, 388.15036599064837, 322.10687912834356]},
            250: {'t': tiempo_2, 'I': [11748.975549395318, 5623.413251903499, 4477.133041763624, 3732.5015779572095, 2471.72414501613, 2051.162178825565, 1374.041975012516, 1180.3206356517303, 851.1380382023776, 749.8942093324565, 552.0774392807579, 485.28850016212147, 402.71703432545945]},
            315: {'t': tiempo_2, 'I': [15488.166189124853, 7079.457843841383, 5610.479760324709, 4655.860935229593, 3097.4192992165836, 2552.701302661249, 1725.8378919902048, 1479.1083881682086, 1078.9467222298294, 939.7233105646382, 687.0684400142328, 608.135001278718, 509.3308710571956]},
            400: {'t': tiempo_2, 'I': [22908.67652767775, 10000.00000000001, 7585.775750291839, 6194.410750767819, 3908.4089579240235, 3258.3670100200893, 2197.859872784826, 1896.7059212111483, 1361.4446824659506, 1199.49930314938, 868.9604292863023, 770.9034690644304, 645.6542290346559]},
            500: {'t': tiempo_3, 'I': [31622.77660168384, 13335.214321633259, 10162.486928706961, 8336.811846196348, 5432.503314924331, 4456.562483975033, 3019.9517204020176, 2606.153549998898, 1866.3796908346708, 1621.8100973589308, 1172.1953655481307, 1030.3861204416162, 807.2350302488384]},
            630: {'t': tiempo_3, 'I': [39810.71705534974, 18836.490894898037, 14554.590805819682, 11939.88104464275, 8128.305161641007, 6839.116472814298, 4497.798548932884, 3810.6582339377314, 2666.858664521482, 2290.867652767775, 1581.2480392703844, 1352.0725631942773, 1023.2929922807547]},
            800: {'t': tiempo_3, 'I': [56234.13251903495, 24490.632418447498, 18879.913490962947, 15488.166189124853, 10471.285480509003, 8830.799004185646, 5970.352865838369, 5035.006087879056, 3443.4993076333894, 2904.0226544644534, 1972.4227361148548, 1682.674061070469, 1288.2495516931347]},
            1000: {'t': tiempo_3, 'I': [70794.57843841378, 30760.96814740714, 23659.196974857587, 19408.85877592782, 13182.56738556409, 11040.78619902074, 7328.245331389056, 6208.690342300644, 4315.1907682776555, 3689.775985701507, 2477.422057633287, 2074.9135174549115, 1621.8100973589308]},
            1250: {'t': tiempo_3, 'I': [100000.0000000002, 43151.90768277653, 33189.44575526104, 27227.013080779132, 18323.144223712126, 15417.004529495585, 10000.00000000001, 8413.95141645195, 5584.701947368314, 4677.351412871984, 3083.1879502493534, 2612.1613543992084, 2041.7379446695318]}
        }

        ax.loglog(fusibles[self.I_f]['I'], fusibles[self.I_f]
                  ['t'], color=lighten_color(color, 0.75), linestyle='-.', label=f'{self.name}   {round_to_text(self.I_f)}A')


@dataclass
class Termica():
    I_t: float
    I_cc: float
    name: str = field(default="fusible")
    curva: chr = "C"
    I_r: float = 0.8
    t_r: float = 12
    I_sd: float = 0
    t_sd: float = 0.1
    I_i: float = 15
    t_i: float = 0.02

    def plot(self, ax: plt.Axes, color: tuple = None, *args, **kwargs):
        t = np.array([10e6, 60*240, 60*10, 40, 8, 2, 0.8, 0.05,
                      0.03, 0.02, 0.012, 0.003])  # s
        if self.curva == "C":
            I_termica = np.array(
                [1.13, 1.13, 1.25, 1.5, 2, 3, 5, 5, 5.3, 6.4, 90, 100000])
            I_termica = I_termica * self.I_t
        elif self.curva == "M":
            if self.I_sd:
                I_termica = [self.I_r*self.I_t, self.I_r*self.I_t, self.I_sd*self.I_t,
                             self.I_sd*self.I_t, self.I_i*self.I_t, self.I_i*self.I_t, 10e7]
                t = [10e6, self.t_r*self.I_sd*30, self.t_r,
                     self.t_sd, self.t_sd, self.t_i, self.t_i]
            else:
                I_termica = [self.I_r*self.I_t, self.I_r*self.I_t,
                             self.I_i*self.I_t, self.I_i*self.I_t, 10e7]
                t = [10e6, self.t_r*self.I_i*30, self.t_r, self.t_i, self.t_i]

        ax.loglog(I_termica, t, color=lighten_color(color, 0.75), linestyle='--',
                  label=f'{self.name}   {round_to_text(self.I_t)}A')


@dataclass
class Proteccion(Nodo):
    name: str = field(default="protection")
    child: Nodo = None
    fusible: Fusible = None
    termica: Termica = None

    def add_fusible(self, fusible: dict):
        self.fusible = fusible

    def add_termica(self, termica: dict):
        self.termica = termica

    def plot(self, ax: plt.Axes, color: tuple = None, *args, **kwargs):
        if self.fusible is not None:
            self.fusible.plot(ax=ax, color=color, *args, **kwargs)
        if self.termica is not None:
            self.termica.plot(ax=ax, color=color, *args, **kwargs)


@dataclass
class Carga(Nodo, GraphicCreator):
    name: str = field(default="carga")
    P: float = 0
    cos_phi: float = 1
    I_n: float = 0
    max_caida: float = 0.05


@dataclass
class Barra(Nodo, GraphicCreator):
    name: str = field(default="barra")
    children: list = field(default_factory=list)
    I_cc: float = 0

    def add_children(self, children: list):
        self.children = children
        for child in children:
            child.parent = self


@dataclass
class Conductor(Nodo):
    name: str = field(default="conductor")
    child: Nodo = None
    I_adm: float = None
    I_n: float = None
    S: int = None
    K: int = 115

    def new_color(self):
        """
        Devuelve el siguiente color en la paleta
        """
        level = 0
        nodo = self
        cmap = ListedColormap(["#A00000", "#4964AB", "#182239", "black"])
        while nodo.parent is not None:
            if isinstance(nodo, Conductor):
                level += 1
            nodo = nodo.parent

        # return cmap(4 - level % 4)
        return plt.cm.tab10(level % 10)

    def plot(self, ax: plt.Axes, color: tuple = None, *args, **kwargs):
        t = np.logspace(-3, 6)  # s
        I_adm = self.K * self.S / np.sqrt(t)  # A
        for i in range(len(I_adm)):
            if I_adm[i] < self.I_adm:
                I_adm[i] = self.I_adm
        ax.loglog(I_adm, t, color=lighten_color(color, 0.5), linestyle='-',
                  label=f'{self.name}   {round_to_text(self.S)}mm²')
        ax.plot([self.I_n, self.I_n], [0.001, 1e6], color=color, linestyle=':',
                label=f'I_n={round_to_text(self.I_n)}A')


# Ejercicio Ema pag 328:
#                        I_carga    I_cond  I_selec     I_termica       I_Corte     I_select_f  I_f     I_cc        I_ccMax
# Térmica del TS5       [25.53,     256,    64,         Sica 63,        10,         75.6,       80,     68.67,      9.9]
# Térmica del TSS8      [15.64,     87,     32,         Sica 32,        3,          38.4,       40,     6.757,      2.7]
# Térmica del CAS 5.12  [9.17,      26,     11,         Sica 16,        3,          0,          0,      0,          0]

def ejemplo_ema_pag_238():
    red = Red()
    barra_ts5 = Barra(I_cc=68.67e6)
    proteccion_ts5 = Proteccion(
        fusible=Fusible(I_f=80),
        termica=Termica(I_t=63, I_cc=10e3))
    conductor_ts5 = Conductor(S=70, I_adm=256, I_n=25.53)
    barra_tss8 = Barra(I_cc=6.757e6)
    proteccion_tss8 = Proteccion(
        fusible=Fusible(I_f=40),
        termica=Termica(I_t=32, I_cc=3e3))
    conductor_tss8 = Conductor(S=10, I_adm=87, I_n=15.64)
    barra_cas = Barra(I_cc=0e6)
    proteccion_cas = Proteccion(
        termica=Termica(I_t=16, I_cc=3e3))
    conductor_cas = Conductor(S=2.5, I_adm=26, I_n=9.17)
    carga = Carga(I_n=53, P=30e3, cos_phi=0.9)

    red.add_child(barra_ts5)
    barra_ts5.add_child(proteccion_ts5)
    proteccion_ts5.add_child(conductor_ts5)
    conductor_ts5.add_child(barra_tss8)
    barra_tss8.add_child(proteccion_tss8)
    proteccion_tss8.add_child(conductor_tss8)
    conductor_tss8.add_child(barra_cas)
    barra_cas.add_child(proteccion_cas)
    proteccion_cas.add_child(conductor_cas)
    conductor_cas.add_child(carga)

    print(red)
    fig = carga.create_plot()
    fig.show()


if __name__ == "__main__":
    ejemplo_ema_pag_238()
