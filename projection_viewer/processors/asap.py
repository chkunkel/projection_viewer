import os


def abcd_exec_query_and_run_asap(query_string):
    """
    Executes the given query in ABCD and runs asap on it, then returns the filename of the final xyz to be read in.

    Note:
        This is very much in development, proof of concept really.
    """

    # exec ABCD download
    abcd_fn = 'raw_abcd_data.xyz'
    abcd_command = "abcd download {fn} -f xyz -q {qq}".format(qq=query_string, fn=abcd_fn)
    os.system(abcd_command)

    # exec ASAP gen_soap_descriptors.py
    desc_executeable = "python /home/tks32/work/ASAP/asap/gen_soap_descriptors.py"
    asap_soap_command = "{ex} -fxyz {fn} --l 8 --n 6 --g 0.5 --periodic True --rcut 4.5 " \
                        "--peratom True".format(fn=abcd_fn, ex=desc_executeable)
    os.system(asap_soap_command)

    # exec ASAP pca_minimal.py
    pca_executeable = "python /home/tks32/work/ASAP/asap/pca_minimal.py"
    final_fn = "ASAP-pca-d4-new.xyz"
    asap_pca_command = "{ex} --desc-key SOAP-n6-l8-c4.5-g0.5 --fxyz ASAP-n6-l8-c4.5-g0.5.xyz --output " \
                       "{fn} -d 4 --scale True --peratom True".format(fn=final_fn, ex=pca_executeable)
    os.system(asap_pca_command)

    return final_fn
