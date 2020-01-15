import os


def abcd_exec_query_and_run_asap(query_string, peratom=True, soap_n=6, soap_l=8, soap_rcut=4.5, soap_g=0.5):
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
    abcd_command = 'abcd download {fn} -f xyz -q "{qq}"'.format(qq=query_string, fn=abcd_fn)
    os.system(abcd_command)

    # exec ASAP gen_soap_descriptors.py
    desc_executeable = "python /home/tks32/work/ASAP/asap/gen_soap_descriptors.py"
    asap_soap_command = "{ex} -fxyz {fn} --l {l} --n {n} --g {g} --periodic True --rcut {cut} " \
                        "--peratom {peratom}".format(fn=abcd_fn, ex=desc_executeable, peratom=peratom, g=soap_g,
                                                     n=soap_n, l=soap_l, cut=soap_rcut)
    os.system(asap_soap_command)

    # exec ASAP pca_minimal.py
    pca_executeable = "python /home/tks32/work/ASAP/asap/pca_minimal.py"
    final_fn = "ASAP-pca-d4-new.xyz"
    asap_pca_command = "{ex} --desc-key {key} --fxyz {in_fn} --output {fn} -d 4 --scale True " \
                       "--peratom {peratom}".format(fn=final_fn, ex=pca_executeable, peratom=peratom, in_fn=foutput,
                                                    key=desc_name)
    os.system(asap_pca_command)

    # the default commands, that are produced now
    # python /home/tks32/work/ASAP/asap/gen_soap_descriptors.py -fxyz raw_abcd_data.xyz
    #                       --l 8 --n 6 --g 0.5 --periodic True --rcut 4.5 --peratom True
    # python /home/tks32/work/ASAP/asap/pca_minimal.py --output ASAP-pca-d4-new.xyz
    #                       -d 4 --scale True --peratom True --desc-key SOAP-n6-l8-c4.5-g0.5 --fxyz ASAP-n6-l8-c4.5-g0.5.xyz

    return final_fn
