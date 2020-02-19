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


def abcd_exec_query_and_run_asap(query_string, peratom=False, soap_n=6, soap_l=8, soap_rcut=4.5, soap_g=0.5):
    """
    Executes the given query in ABCD and runs asap on it, then returns the filename of the final xyz to be read in.

    Note:
        This is very much in development, proof of concept really.
    """
    # naming conventions from ASAP fixme: add a parameter of filename to ASAP instead, not hack in here
    foutput = 'ASAP-n{0}-l{1}-c{2}-g{3}.xyz'.format(str(soap_n), str(soap_l), str(soap_rcut), str(soap_g))
    desc_name = "SOAP-n{0}-l{1}-c{2}-g{3}".format(str(soap_n), str(soap_l), str(soap_rcut), str(soap_g))

    # process the query string
    query_string = query_string.replace('\n', ' ')
    query_string = query_string.replace('"', '\\"')

    # exec ABCD download
    abcd_fn = 'raw_abcd_data.xyz'
    abcd_download(abcd_fn, query_string)

    # exec ASAP gen_soap_descriptors.py
    asap_soap_command = ["gen_soap_descriptors.py",
                         "-fxyz={}".format(abcd_fn),
                         "--l={}".format(soap_l),
                         "--n={}".format(soap_n),
                         "--g={}".format(soap_g),
                         "--periodic={}".format(True),
                         "--rcut={}".format(soap_rcut),
                         "--peratom={}".format(peratom)]
    run(asap_soap_command)

    # exec ASAP pca_minimal.py
    final_fn = "ASAP-pca-d4-new.xyz"
    asap_pca_command = ["pca_minimal.py",
                        "--desc-key={}".format(desc_name),
                        "--fxyz={}".format(foutput),
                        "--output={}".format(final_fn),
                        "-d=4",
                        "--scale={}".format(True),
                        "--peratom={}".format(peratom)]

    run(asap_pca_command)

    return final_fn
