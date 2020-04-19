from subprocess import run as r


def run(cmd, *args, **kwargs):
    cmd = [str(c) for c in cmd]
    print('DEBUG: running command --- ', cmd)
    r(cmd, *args, **kwargs)


def abcd_download(fn, query_string):
    # exec ABCD download
    abcd_command = ['abcd', 'download', fn, '-f', 'xyz', '-q', query_string]
    run(abcd_command)


def no_processor(query_string):
    abcd_fn = 'raw_abcd_data.xyz'
    abcd_download(abcd_fn, query_string)
    return abcd_fn


def abcd_exec_query_and_run_asap(query_string, mode_value="molecular",
                                 soap_n=6, soap_l=8, soap_rcut=4.5, soap_g=0.5, d=4, soap_zeta=2.0, soap_periodic=True):
    """
    Executes the given query in ABCD and runs asap on it, then returns the filename of the final xyz to be read in.

    Note:
        This is very much in development, proof of concept really.
    """
    # mode to bool
    peratom = mode_value == "atomic"

    # process the query string
    query_string = query_string.replace('\n', ' ')
    query_string = query_string.replace('"', '\\"')

    # exec ABCD download
    abcd_fn = 'raw_abcd_data.xyz'
    abcd_download(abcd_fn, query_string)

    # exec ASAP kpca_for_projection_viewer.py
    final_fn = "ASAP-pca-d4-new.xyz"
    asap_pca_command = ["kpca_for_projection_viewer.py",
                        # file stuff
                        "-fxyz={}".format(abcd_fn),
                        "--output={}".format(final_fn),
                        # soap & projection stuff
                        "--d={}".format(d),
                        "--rcut={}".format(soap_rcut),
                        "--n={}".format(soap_n),
                        "--l={}".format(soap_l),
                        "--g={}".format(soap_g),
                        "--zeta={}".format(soap_zeta),
                        "--periodic={}".format(soap_periodic),
                        "--peratom={}".format(peratom)
                        ]

    run(asap_pca_command)

    return final_fn
