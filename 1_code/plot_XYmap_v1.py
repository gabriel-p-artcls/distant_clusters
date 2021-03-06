
"""
Plot the clusters in all four databases in the context of the Milky Way
"""


from astropy import units as u
from astropy.coordinates import SkyCoord
import astropy.coordinates as coord
from astropy.io import ascii
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
from plot_pars import dpi, grid_x, grid_y, sc_sz, sc_ec, sc_lw


# Shorlin1     166.44 -61.23 .8  nan   nan   nan   nan  nan   12600 6.5   5594
# FSR0338      327.93 55.33  2.7 8.1   14655 nan   nan  nan   nan    8.1  14655
lit_data = """
Cluster      RA  DEC       Dm  A_OC02  D_OC02  A_CG20 D_CG20  A_WEBDA  D_WEBDA  A_MWSC  D_MWSC
Ber73        95.50  -6.35  2   9.18  9800  9.15 6158  9.36  6850  9.15  7881
Ber25        100.25 -16.52 5   9.7   11400 9.39 6780  9.6   11300 9.7   11400
Ber75        102.25 -24.00 4   9.6   9100  9.23 8304  9.48  9800  9.3   6273
Ber26        102.58 5.75   4   9.6   12589 nan   nan  9.6   4300  8.71  2724
Ber29        103.27 16.93  6   9.025 14871 9.49 12604 9.025 14871 9.1   10797
Tombaugh2    105.77 -20.82 3   9.01  6080  9.21 9316  9.01  13260 9.01  6565
Ber76        106.67 -11.73 5   9.18  12600 9.22 4746  9.18  12600 8.87  2360
FSR1212      106.94 -14.15 nan nan   nan   9.14 9682  nan   nan   8.65  1780
Saurer1      110.23 1.81   4   9.7   13200 nan   nan  9.85  13200 9.6   13719
Czernik30    112.83 -9.97  3   9.4   9120  9.46 6647  9.4   6200  9.2   6812
arpm2        114.69 -33.84 2   9.335 13341 9.48 11751 9.335 13341 9.335 13338
vdBH4        114.43 -36.07 2   nan   nan   nan  nan   8.3   19300 nan   nan
FSR1419      124.71 -47.79 nan nan   nan   9.21 11165 nan   nan   8.375 7746
vdBH37       128.95 -43.62 3   8.84  11220 8.24 4038  8.85  2500  7.5   5202
ESO09205     150.81 -64.75 5   9.3   5168  9.65 12444 9.78  10900 9.3   5168
ESO09218     153.74 -64.61 5   9.024 10607 9.46 9910  9.024 607   9.15  9548
Saurer3      160.35 -55.31 4   9.3   9550  nan   nan  9.45  8830  9.3   7075
Kronberger39 163.56 -61.74 .8  nan   11100 nan   nan  nan   nan   6.    4372
ESO09308     169.92 -65.22 1   9.74  14000 nan   nan  9.65  3700   9.8  13797
vdBH144      198.78 -65.92 1.5 8.9   12000 9.17 9649  8.9   12000  9    7241
vdBH176      234.85 -50.05 3   nan   nan   nan   nan  nan   13400  9.8  18887
Kronberger31 295.05 26.26  1.3 nan   11900 nan   nan  nan   nan    8.5  12617
Saurer6      297.76 32.24  1.8 9.29  9330  nan   nan  9.29  9330   9.2  7329
Ber56        319.43 41.83  3   9.6   12100 9.47 9516  9.6   12100  9.4  13180
Ber102       354.66 56.64  5   9.5   9638  9.59 10519 8.78  2600   9.14 4900
"""

out_folder = '../2_pipeline/plots/'


def main(dpi=dpi):
    """
    Gridspec idea: http://www.sc.eso.org/~bdias/pycoffee/codes/20160407/
                   gridspec_demo.html
    """
    data = ascii.read(lit_data)
    DBs_list = ('D_MWSC', 'D_WEBDA', 'D_OC02', 'D_CG20')

    # # Use this block to plot the ASteCA results instead
    # # ASteCA output data
    # if plot_ASteCA:
    #     asteca_data = ascii.read(
    #         '../2_pipeline/5_ASteCA/out/asteca_output.dat')
    #     asteca_names = list([_[3:].upper() for _ in asteca_data['NAME']])
    #     asteca_dists = []
    #     for cl in data['Cluster']:
    #         try:
    #             idx = asteca_names.index(cl.upper())
    #             d_pc = 10**(.2 * (asteca_data[idx]['d_mean'] + 5))
    #         except ValueError:
    #             d_pc = np.nan
    #         asteca_dists.append(round(d_pc, 0))
    #     data['D_AS'] = asteca_dists
    #     DBs_list = ('D_AS',)

    # Default Galactic Center is 8.3 kpc (Gillessen et al. 2009)
    gc_frame = coord.Galactocentric()

    # Obtain latitude, longitude
    eq = SkyCoord(
        ra=data['RA'] * u.degree, dec=data['DEC'] * u.degree,
        frame='icrs')
    lb = eq.transform_to('galactic')
    lon = lb.l.wrap_at(180 * u.deg).radian * u.radian
    lat = lb.b.radian * u.radian

    xyz_kpc = {}
    for cat in DBs_list:
        xyz_kpc[cat] = xyzCoords(data, cat, lon, lat, gc_frame)

    for i, cl in enumerate(data['Cluster']):
        x_dist, y_dist, z_dist, R_GC = "", "", "", ""
        for cat in DBs_list:
            x_dist += " {:>6.2f}".format(xyz_kpc[cat][0][i].value)
            y_dist += " {:>6.2f}".format(xyz_kpc[cat][1][i].value)
            z_dist += " {:>6.2f}".format(xyz_kpc[cat][2][i].value)
            RGC = np.sqrt(
                xyz_kpc[cat][0][i]**2 + xyz_kpc[cat][1][i]**2
                + xyz_kpc[cat][2][i]**2)
            R_GC += " {:>6.2f}".format(RGC.value)
        # print("{:<15}".format(cl), x_dist, y_dist, z_dist)
        print("{:<15}".format(cl), R_GC)

    # Sun's coords according to the Galactocentric frame.
    x_sun, z_sun = gc_frame.galcen_distance, gc_frame.z_sun
    s_xys = SkyCoord(
        -x_sun, 0., z_sun, unit='kpc', representation_type='cartesian')

    # colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    colors = sns.color_palette("Spectral", 13)[2::3]
    # colors = sns.color_palette("Set2")
    # colors = sns.color_palette("Paired")[::2]
    # colors = sns.color_palette("cubehelix", 10)[::2]

    markers = ('o', '*', 'v', '^')
    Xmin, Xmax, Ymin, Ymax, Zmin, Zmax = -24, 11, -19, 16, -2.6, 2.6

    fig = plt.figure(figsize=(17, 17))
    gs = gridspec.GridSpec(grid_y, grid_x)

    plt.subplot(gs[0:4, 0:4])
    # plt.grid(ls=':', c='grey', lw=.5, zorder=.5)
    plt.axhline(0, ls=':', c='grey', zorder=-1)
    plt.axvline(0, ls=':', c='grey', zorder=-1)

    cl_plots1 = [[], []]
    for ic, cat in enumerate(DBs_list):
        x_kpc, y_kpc, z_kpc = xyz_kpc[cat]
        pl = plt.scatter(
            x_kpc, y_kpc, alpha=.8, marker=markers[ic], s=sc_sz * 2,
            lw=sc_lw, edgecolor=sc_ec, zorder=2.5, color=colors[ic])
        cl_plots1[0].append(pl)
        cl_plots1[1].append(cat.replace('D_', ''))

    # Plot Sun and center of Milky Way
    plt.scatter(s_xys.x, s_xys.y, c='yellow', s=50, edgecolor='k', zorder=2.5)
    plt.scatter(0., 0., c='k', marker='o', s=150, zorder=2.5)
    # Plot spiral arms
    cl_plots2 = plotSpiral()

    l1 = plt.legend(cl_plots1[0], cl_plots1[1], loc=1, fontsize=12)
    plt.legend(cl_plots2[0], cl_plots2[1], loc=4, fontsize=12)
    plt.gca().add_artist(l1)
    plt.xlim(Xmin, Xmax)
    plt.ylim(Ymin, Ymax)
    plt.xlabel(r"$x_{GC}$ [Kpc]", fontsize=15)
    plt.ylabel(r"$y_{GC}$ [Kpc]", fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    #
    # X_GC vs Z_GC
    # plt.subplot(gs[4:6, 0:4])
    plt.subplot(gs[0:2, 4:8])
    for ic, cat in enumerate(DBs_list):
        x_kpc, y_kpc, z_kpc = xyz_kpc[cat]
        plt.scatter(
            x_kpc, z_kpc, alpha=.8, color=colors[ic], marker=markers[ic],
            s=100, lw=.5, edgecolor='k', zorder=2.5)
    plt.axvline(0, ls=':', c='grey', zorder=-1)
    plt.axhline(0, ls=':', c='grey', zorder=-1)
    plt.scatter(s_xys.x, s_xys.z, c='yellow', s=50, edgecolor='k', zorder=5)
    plt.scatter(0., 0., c='k', marker='o', s=150, zorder=5)
    plt.xlabel(r"$x_{GC}\, [Kpc]$", fontsize=15)
    plt.ylabel(r"$z_{GC}\, [Kpc]$", fontsize=15)
    plt.xlim(Xmin, Xmax)
    plt.ylim(Zmin, Zmax)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    #
    # Y_GC vs Z_GC
    # plt.subplot(gs[6:8, 0:4])
    plt.subplot(gs[2:4, 4:8])
    for ic, cat in enumerate(DBs_list):
        x_kpc, y_kpc, z_kpc = xyz_kpc[cat]
        plt.scatter(
            y_kpc, z_kpc, alpha=.8, color=colors[ic], marker=markers[ic],
            s=100, lw=.5, edgecolor='k', zorder=2.5)
    plt.axvline(0, ls=':', c='grey', zorder=-1)
    plt.axhline(0, ls=':', c='grey', zorder=-1)
    plt.scatter(0., 0., c='k', marker='o', s=150, zorder=4)
    plt.scatter(s_xys.y, s_xys.z, c='yellow', s=50, edgecolor='k', zorder=5)
    plt.xlabel(r"$y_{GC}\, [Kpc]$", fontsize=15)
    plt.ylabel(r"$z_{GC}\, [Kpc]$", fontsize=15)
    plt.xlim(Ymin, Ymax)
    plt.ylim(Zmin, Zmax)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    fig.tight_layout()
    plt.savefig(out_folder + 'MWmap.png', bbox_inches='tight', dpi=dpi)


def xyzCoords(data, cat, lon, lat, gc_frame):
    """
    """
    try:
        dist_pc = data[cat].filled(np.nan)
    except AttributeError:
        dist_pc = data[cat]
    dist_pc = dist_pc / 1000.

    # Galactic coordinates.
    coords = SkyCoord(l=lon, b=lat, distance=dist_pc * u.kpc, frame='galactic')

    # Galactocentric coordinates.
    c_glct = coords.transform_to(gc_frame)

    # Rectangular coordinates
    x_kpc, y_kpc, z_kpc = c_glct.x, c_glct.y, c_glct.z

    return x_kpc, y_kpc, z_kpc


def plotSpiral():
    """
    """
    spiral_arms = momany()

    cl_plots = [[], []]
    for sp_name, vals in spiral_arms.items():
        xy_arm = np.array(list(zip(*vals)))
        if sp_name == 'Outer':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c="#0B5CA4", ls='-.', lw=2, zorder=-1)
        if sp_name == 'Perseus':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c='orange', ls='--', lw=2, zorder=-1)
        if sp_name == 'Orion-Cygnus':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c='k', ls="-", lw=2, zorder=-1)
        elif sp_name == 'Carina-Sagittarius':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c='b', ls=':', lw=2, zorder=-1)
        elif sp_name == 'Crux-Scutum':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c='purple', ls='-.', lw=2, zorder=-1)
        elif sp_name == 'Norma':
            pl, = plt.plot(
                xy_arm[0], xy_arm[1], c='green', ls=':', lw=2, zorder=-1)
        cl_plots[0].append(pl)
        cl_plots[1].append(sp_name)

    return cl_plots


def momany():
    """
    Obtained from Momany et al. (2006) "Outer structure of the..."
    """
    spiral_arms = {
        'Outer': (
            (7.559999999999999, 2.514124293785308),
            (7.237333333333332, 3.4180790960452008),
            (6.738666666666667, 4.46327683615819),
            (6.1519999999999975, 5.480225988700564),
            (5.535999999999998, 6.384180790960453),
            (4.861333333333334, 7.1186440677966125),
            (4.479999999999997, 7.514124293785311),
            (3.8053333333333335, 7.909604519774014),
            (2.8373333333333335, 8.474576271186443),
            (1.751999999999999, 9.011299435028253),
            (0.6373333333333306, 9.35028248587571),
            (-0.4480000000000022, 9.63276836158192),
            (-1.2693333333333356, 9.830508474576273),
            (-1.8560000000000016, 9.943502824858761),
            (-2.677333333333337, 10),
            (-3.4986666666666686, 9.943502824858761),
            (-4.085333333333336, 9.915254237288138),
            (-5.024000000000003, 9.830508474576273),
            (-5.845333333333336, 9.689265536723166),
            (-6.4906666666666695, 9.519774011299436),
            (-7.253333333333337, 9.322033898305087),
            (-7.986666666666669, 8.926553672316388),
            (-8.485333333333337, 8.559322033898308),
            (-9.160000000000004, 8.050847457627121),
            (-9.864000000000004, 7.570621468926557),
            (-10.333333333333336, 7.203389830508474),
            (-10.89066666666667, 6.525423728813561),
            (-11.389333333333337, 5.9604519774011315),
            (-11.77066666666667, 5.395480225988699),
            (-12.240000000000004, 4.661016949152543),
            (-12.65066666666667, 3.9830508474576263),
            (-13.061333333333337, 3.361581920903955),
            (-13.442666666666671, 2.7401129943502838)),
        'Perseus': (
            (5.2719999999999985, 2.372881355932204),
            (4.9786666666666655, 3.27683615819209),
            (4.773333333333333, 3.6723163841807924),
            (4.3039999999999985, 4.46327683615819),
            (3.776, 5.141242937853107),
            (3.3359999999999985, 5.593220338983052),
            (2.690666666666665, 6.073446327683616),
            (2.074666666666662, 6.468926553672318),
            (1.4879999999999995, 6.751412429378529),
            (0.607999999999997, 7.005649717514125),
            (-0.15466666666666917, 7.146892655367235),
            (-0.8293333333333344, 7.259887005649716),
            (-1.621333333333336, 7.316384180790962),
            (-2.4426666666666694, 7.288135593220339),
            (-3.14666666666667, 7.1186440677966125),
            (-3.909333333333336, 7.005649717514125),
            (-4.6426666666666705, 6.666666666666668),
            (-5.3173333333333375, 6.3559322033898304),
            (-5.962666666666669, 5.903954802259886),
            (-6.57866666666667, 5.395480225988699),
            (-6.989333333333336, 5.028248587570623),
            (-7.63466666666667, 4.350282485875709),
            (-8.104000000000003, 3.7570621468926575),
            (-8.51466666666667, 3.10734463276836),
            (-8.896000000000004, 2.4011299435028235),
            (-9.218666666666671, 1.6384180790960414),
            (-9.424000000000003, 1.073446327683616),
            (-9.65866666666667, 0.1977401129943459),
            (-9.805333333333337, -0.5084745762711869),
            (-9.92266666666667, -0.8192090395480243),
            (-10.010666666666669, -1.2711864406779654),
            (-10.128000000000004, -2.005649717514128),
            (-10.186666666666671, -2.711864406779661),
            (-10.186666666666671, -2.909604519774014),
            (-10.128000000000004, -3.3615819209039586),
            (-9.952000000000004, -4.2372881355932215),
            (-9.83466666666667, -5),
            (-9.688000000000002, -5.310734463276839),
            (-9.48266666666667, -5.734463276836161),
            (-9.189333333333337, -6.29943502824859),
            (-8.86666666666667, -7.005649717514126),
            (-8.456000000000003, -7.598870056497178)),
        'Orion-Cygnus': (
            (-7.341333333333337, 3.2485875706214706),
            (-7.63466666666667, 2.909604519774014),
            (-7.9280000000000035, 2.485875706214692),
            (-8.280000000000003, 1.9209039548022595),
            (-8.456000000000003, 1.4124293785310726),
            (-8.60266666666667, 1.1016949152542352),
            (-8.808000000000003, 0.5649717514124291),
            (-9.013333333333335, -0.197740112994353),
            (-9.13066666666667, -0.7627118644067821),
            (-9.160000000000004, -1.2146892655367267)),
        'Carina-Sagittarius': (
            (2.8373333333333335, 3.6723163841807924),
            (2.5146666666666633, 4.152542372881356),
            (2.338666666666665, 4.350282485875709),
            (1.9280000000000008, 4.774011299435031),
            (1.2239999999999966, 5.16949152542373),
            (0.49066666666666237, 5.451977401129945),
            (-0.12533333333333552, 5.593220338983052),
            (-0.7706666666666688, 5.621468926553675),
            (-1.7680000000000025, 5.53672316384181),
            (-2.5600000000000023, 5.310734463276834),
            (-2.970666666666668, 5.112994350282488),
            (-3.645333333333337, 4.576271186440678),
            (-3.8800000000000026, 4.350282485875709),
            (-4.2613333333333365, 3.9830508474576263),
            (-4.613333333333337, 3.5593220338983045),
            (-4.789333333333337, 3.192090395480225),
            (-5.1413333333333355, 2.627118644067796),
            (-5.493333333333336, 2.033898305084744),
            (-5.845333333333336, 1.4124293785310726),
            (-6.22666666666667, 0.6497175141242906),
            (-6.608000000000002, -0.14124293785311082),
            (-6.842666666666668, -0.7627118644067821),
            (-7.048000000000004, -1.5536723163841835),
            (-7.19466666666667, -2.25988700564972),
            (-7.253333333333337, -3.1073446327683634),
            (-7.136000000000003, -3.6440677966101696),
            (-7.048000000000004, -3.98305084745763),
            (-6.813333333333338, -4.519774011299436),
            (-6.461333333333336, -5.254237288135597),
            (-6.05066666666667, -5.875706214689268),
            (-5.6106666666666705, -6.440677966101699),
            (-5.024000000000003, -6.977401129943505),
            (-4.466666666666669, -7.485875706214692),
            (-3.8800000000000026, -7.909604519774014),
            (-3.352000000000002, -8.163841807909607),
            (-3.0880000000000027, -8.361581920903957)),
        'Crux-Scutum': (
            (1.663999999999998, 3.1355932203389827),
            (1.3119999999999976, 3.4180790960452008),
            (0.6666666666666643, 3.8135593220338997),
            (-0.09600000000000186, 3.9830508474576263),
            (-0.858666666666668, 4.0395480225988685),
            (-1.5626666666666686, 3.926553672316384),
            (-2.2666666666666693, 3.5875706214689274),
            (-2.9413333333333362, 3.192090395480225),
            (-3.5280000000000022, 2.6553672316384187),
            (-3.909333333333336, 2.033898305084744),
            (-4.29066666666667, 1.3276836158192076),
            (-4.584000000000003, 0.6214689265536713),
            (-4.760000000000003, -0.11299435028248794),
            (-4.906666666666668, -0.9322033898305087),
            (-4.965333333333335, -1.6666666666666714),
            (-4.994666666666669, -2.344632768361585),
            (-4.8480000000000025, -3.2203389830508478),
            (-4.672000000000002, -3.8983050847457648),
            (-4.320000000000004, -4.576271186440678),
            (-3.8800000000000026, -5.225988700564974),
            (-3.4106666666666694, -5.734463276836161),
            (-2.765333333333336, -6.158192090395483),
            (-2.032000000000002, -6.610169491525427),
            (-1.3866666666666685, -6.920903954802263),
            (-0.6826666666666696, -7.06214689265537),
            (0.05066666666666464, -7.25988700564972),
            (0.8719999999999999, -7.401129943502829),
            (1.575999999999997, -7.372881355932208),
            (2.2799999999999976, -7.316384180790964)),
        'Norma': (
            (-3.14666666666667, 0.8474576271186436),
            (-3.3226666666666684, 0.1977401129943459),
            (-3.2933333333333366, -0.7627118644067821),
            (-3.2346666666666692, -1.4406779661016955),
            (-2.970666666666668, -2.1186440677966125),
            (-2.5600000000000023, -2.824858757062149),
            (-2.1200000000000028, -3.4463276836158236),
            (-1.6506666666666696, -3.9548022598870105),
            (-0.9760000000000026, -4.378531073446332),
            (-0.2720000000000038, -4.689265536723166),
            (0.4319999999999986, -4.858757062146896),
            (0.9600000000000009, -4.887005649717519),
            (1.370666666666665, -4.858757062146896),
            (2.0453333333333283, -4.717514124293789),
            (2.6613333333333316, -4.519774011299436),
            (3.042666666666662, -4.406779661016952),
            (3.4826666666666632, -4.152542372881356),
            (4.010666666666662, -3.7288135593220346),
            (4.538666666666664, -3.050847457627121))
    }

    return spiral_arms


if __name__ == '__main__':
    plt.style.use('science')
    main()
