import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import sys,os
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'include'))
sys.path.insert(0, include_path)
import db_init as db
from utils import *
import matplotlib as mpl
import matplotlib.pyplot as plt


def labelScatterPlot(labels, ax, xs, ys, stdn, printLabel):
    df = pd.DataFrame({'xs': xs, 'ys': ys}, index=labels)
    stdx, stdy = df['xs'].std(), df['ys'].std()
    df = df.loc[(df['xs'] >= stdx * stdn) | (df['xs'] <= -(stdx * stdn)) | (df['ys'] >= stdy * stdn) | (
                df['ys'] <= -(stdy * stdn))]

    df = df.sort_values('xs', ascending=False)
    textobjs = list()
    for label, data in df.iterrows():
        textobj = ax.text(data['xs'], data['ys'], label, fontsize=8, alpha=1, zorder=10, ha='center', va='center')
        textobjs.append(textobj)
    return textobjs

def read_node_csv(node_file):
    df = pd.read_csv(node_file)
    df = df.set_index('id_node')
    df['token'] = dfD['token']
    df['type'] = dfD['type']
    return df

def calc_pca(nodefile, edgefile, network, normalize, source, dicttimestamp):
    only_metric = False
    if network in ['d', 'distance']:
        match_edge = {'original': True}
        weight = 'distance'
        #
        network_short = 'dist'
        convert_inf_to_max = True

    elif network in ['p', 'proximity']:
        match_edge = {'original': True}
        weight = 'proximity'
        #
        network_short = 'prox'
        convert_inf_to_max = False

    elif network in ['dmc', 'distance metric closure', 'all']:
        match_edge = {'original': True}
        weight = 'distance'
        #
        network_short = 'dist-m-c'
        convert_inf_to_max = True

    elif network in ['dmb', 'distance metric backbone']:
        match_edge = {'metric_backbone': True}
        only_metric = True
        weight = 'distance'
        #
        network_short = 'dist-m-bb'
        convert_inf_to_max = True

    elif network in ['pmb', 'proximity metric backbone']:
        match_edge = {'metric_backbone': True}
        only_metric = True
        weight = 'proximity'
        #
        network_short = 'prox-m-bb'
        convert_inf_to_max = False
    dfN = read_node_csv(nodefile)
    dfE = pd.read_csv(edgefile)
    if only_metric:
        dfE = dfE[dfE['is_metric']]

    # wPCAFile = 'results/{}/{}/pca/pca-{}-{}-{}-{}D-{}-dim.csv'.format(cohort, socialmedia, cohort, socialmedia,
    #                                                                   dicttimestamp, window_size, network_short)
    # wSFile = 'results/{}/{}/pca/pca-{}-{}-{}-{}D-{}-s.csv'.format(cohort, socialmedia, cohort, socialmedia,
    #                                                               dicttimestamp, window_size, network_short)

    wPCAFile = 'results/{}/pca/pca-{}-{}-{}-dim.csv'.format(source, source, dicttimestamp, network_short)
    wSFile = 'results/{}/pca/pca-{}-{}-{}-s.csv'.format(source, source, dicttimestamp, network_short)

    # Make Adjacency Matrix
    dfX = dfE.pivot(index='source', columns='target', values=weight)
    idx = dfN.index  # make symmetric
    dfX = dfX.reindex(index=idx, columns=idx, fill_value=0).fillna(0)

    print("--- Calculating PCA on '{}' ---".format(weight))
    X = dfX.values

    if convert_inf_to_max:
        print('> Converting inf to max()')
        # X[X==np.nan] = np.inf
        X[X == np.inf] = -1
        nmax = X.max()
        X[X == -1] = nmax

    # Normalize
    if normalize:
        print('> Normalizing')
        X = StandardScaler().fit_transform(X)

    # PCA
    print('> PCA')
    pca = PCA(n_components=None)
    res = pca.fit_transform(X)

    # Results
    dfPCA = pd.DataFrame(res[:, 0:9], columns=['1c', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c'], index=dfX.index)
    dfPCA['label'] = dfN['token']  # .index.map(lambda x: dict_token[x])
    dfPCA['type'] = dfN['type']  # .index.map(lambda x: dict_type[x])
    dfPCA['id_original'] = dfN.index  # dfX.index.map(lambda x: dict_id_original[x])

    s = pd.Series(pca.explained_variance_ratio_, index=range(1, res.shape[1] + 1), name='explained_variance_ratio')

    #
    print('> Saving to .CSV -')
    ensurePathExists(wPCAFile)
    ensurePathExists(wSFile)
    #
    dfPCA.to_csv(wPCAFile, encoding='utf-8')
    s.to_csv(wSFile, encoding='utf-8')

    print('Done.')


def plot_pca(network, source, dicttimestamp, ):
    if network not in [
        'd', 'distance',
        'p', 'proximity',
        'dmc', 'distance metric closure',
        'dmb', 'distance metric backbone',
        'pmb', 'proximity metric backbone'
    ]:
        raise TypeError("Nework must be 'distance' or 'proximity'.")

    if network in ['d', 'distance']:

        network = 'Distance'
        network_short = 'dist'

    elif network in ['p', 'proximity']:

        network = 'Proximity'
        network_short = 'prox'

    elif network in ['dmc', 'distance metric closure']:

        network = 'Distance Metric Closure'
        network_short = 'dist-m-c'

    elif network in ['dmb', 'distance metric backbone']:

        network = 'Distance Metric Backbone'
        network_short = 'dist-m-bb'

    elif network in ['pmb', 'proximity metric backbone']:

        network = 'Proximity Metric Backbone'
        network_short = 'prox-m-bb'

    print('--- Plotting PCA: {:s} -  {:s} ---'.format(source,  network))
    #
    # Files
    #
    rPCAFile = 'results/{}/pca/pca-{}-{}-{}-dim.csv'.format(source, source, dicttimestamp, network_short)
    rSFile = 'results/{}/pca/pca-{}-{}-{}-s.csv'.format(source, source, dicttimestamp, network_short)
    wIMGFile = 'images/{}/pca-{}-{}-{}.pdf'.format(source, source, dicttimestamp,
                                                   network_short)

    print('> Loading PCA .csv')
    dfPCA = pd.read_csv(rPCAFile, index_col=0, encoding='utf-8')
    s = pd.read_csv(rSFile, squeeze=True, index_col=0, encoding='utf-8')

    print(dfPCA.head())
    print(s.head())

    # Change Cannabis Type
    dfPCA.loc[dfPCA['label'] == 'Cannabis', 'type'] = 'Cannabis'
    #
    # Plot PCA
    #
    print('> Plotting PCA')

    # colors_dict = {'drug':'red','symp':'blue','herb':'green','cann':'yellow','epil':'magenta'}
    colors_dict = {
        'Drug': 'red',
        'Medical term': 'darkblue',
        'Natural product': 'darkgreen',
        'Cannabis': 'olive',
        # 'Epilepsy':'magenta',
        'Allergen': 'gold',
    }
    dfPCA['color'] = dfPCA['type'].map(colors_dict)

    title = '{}. PCA on {} network\nOnly co-mentions.'.format(source.title(), network)

    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(figsize=(12, 10), nrows=3, ncols=3)
    fig.suptitle(title)
    # plt.rc('font', size=11)
    # plt.rc('legend', fontsize=12)
    # plt.rc('legend', scatterpoints=1)

    #
    # Plot EigenVals
    #
    s_cumsum = s.cumsum()
    n_eigen_95 = s_cumsum[s_cumsum < 0.95].shape[0]

    n = 9
    ind = np.arange(n)
    height = s.iloc[:n].values
    width = 0.60
    xticklabels = ind + 1

    cmap = mpl.cm.get_cmap('hsv_r')
    norm = mpl.colors.Normalize(vmin=0, vmax=n)
    s_colors = list(map(cmap, np.linspace(0, 1, n, endpoint=False)))

    ax1.bar(ind, height, width, color=s_colors, zorder=9, edgecolor='black')
    ax1.set_xticks(ind)
    ax1.set_xticklabels(xticklabels)

    ax1.set_title('Explained variance ratio')
    ax1.annotate('95% with {:d}\nsingular vectors'.format(n_eigen_95), xy=(0.97, 0.97), xycoords="axes fraction",
                 ha='right', va='top')
    ax1.set_xlabel('Components')
    ax1.set_ylabel('%')

    ax1.grid()
    # ax1.set_xlim(-0.25,n-0.25)

    for dim, ax in zip(range(1, 10), [ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]):
        print('> Dim: {:d}'.format(dim))
        col = str(dim) + 'c'
        x = str(dim) + 'c'
        y = str(dim + 1) + 'c'
        xs = dfPCA[x].tolist()
        ys = dfPCA[y].tolist()
        pca_colors = dfPCA['color'].tolist()

        # if pca_colors == None:
        #	pca_colors = ys
        #	norm = mpl.colors.Normalize( vmin=min(ys), vmax=max(ys) )
        #	ax.scatter(xs,ys, c=pca_colors, cmap=cmapR2G2G, norm=norm, marker='o', edgecolor='black', lw=0.5, s=25)
        # else:
        ax.scatter(xs, ys, c=pca_colors, marker='o', edgecolor='black', lw=0.5, s=30, zorder=5, rasterized=True)

        # Draw a X at the center
        # ax.plot(0,0, color='black', marker='x', ms=16)

        # Draw lines at the center
        ax.axhline(y=0, c='black', lw=0.75, ls='-.', zorder=2)
        ax.axvline(x=0, c='black', lw=0.75, ls='-.', zorder=2)

        ax.set_title('Components {} and {}'.format(dim, dim + 1))
        ax.set_xlabel('Component %d' % (dim))
        ax.set_ylabel('Component %d' % (dim + 1))

        ax.grid()
        ax.axis('equal')
        ax.locator_params(axis='both', tight=True, nbins=6)

        # ax.set_aspect('equal')
        # xmin, xmax = ax.get_xlim()
        # ax.set_xticks(np.round(np.linspace(xmin, xmax, 6), 2))
        # ymin, ymax = ax.get_ylim()
        # ax.set_yticks(np.round(np.linspace(ymin, ymax, 6), 2))

        labels = labelScatterPlot(dfPCA['label'].values, ax, xs, ys, stdn=8, printLabel=True)
        # adjust_text(
        #     labels, x=xs, y=ys, ax=ax,
        #     lim=100,
        #     force_text=(.1, .4), force_points=(.1, .4), force_objects=(1, 1),
        #     expand_text=(1.4, 1.8), expand_points=(1.4, 1.8), expand_objects=(1, 1), expand_align=(1.1, 1.9),
        #     only_move={'points': 'xy', 'text': 'xy', 'objects': 'xy'},
        #     text_from_points=True,
        #     ha='center', va='center', autoalign=False,
        #     arrowprops=dict(arrowstyle="->", shrinkB=5, color='gray', lw=0.5, connectionstyle='angle3'),
        # )

    # Save
    ensurePathExists(wIMGFile)
    plt.subplots_adjust(left=0.06, right=0.98, bottom=0.06, top=0.9, wspace=0.32, hspace=0.35)
    plt.savefig(wIMGFile, dpi=150, bbox_inches=None, pad_inches=0.0)
    plt.close()


if __name__ == '__main__':
    dicttimestamp = '20180706'
    engine = db.connectToPostgreSQL(server='cns-postgres-myaura')
    tablename = 'dictionaries.dict_%s' % (dicttimestamp)
    sql = """
        SELECT
            d.id,
            COALESCE(d.id_parent,d.id) AS id_parent,
            d.dictionary,
            d.token,
            COALESCE(p.token, d.token) as parent,
            d.type,
            d.source,
            d.id_original,
            COALESCE(p.id_original, d.id_original) as id_original_parent
            FROM %s d
            LEFT JOIN %s p ON d.id_parent = p.id
            """ % (tablename, tablename)
    dfD = pd.read_sql(sql, engine, index_col='id')
    for dicttimestamp in ['20180706', '20210321']:
        for base_name, data_name in \
                [['tmp-data/ct-epilepsy-network-xxxxx-yyyy.csv', 'CT'],
                 ['tmp-data/04-instagram-epilepsy-network-xxxxx-samepost-yyyy.csv', 'instagram'],
                 ['tmp-data/04-efwebsite-forums-network-xxxxx-samepost-yyyy.csv', 'EFF'],
                 ['tmp-data/04-pubmed-epilepsy-network-xxxxx-yyyy.csv', 'PubMed']]:
            node_file = base_name.replace('xxxxx', dicttimestamp).replace('yyyy', 'nodes')
            edge_file = base_name.replace('xxxxx', dicttimestamp).replace('yyyy', 'edges')
            for measure, norm in [['d', True], ['p', True], ['dmb', True], ['pmb', True]]:
                calc_pca(node_file, edge_file, measure, norm, data_name, dicttimestamp)
                plot_pca(measure, data_name, dicttimestamp)