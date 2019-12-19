tooltips = {}

tooltips['compound'] = """
        <div>
                <img
                    src="@p_images" height="220" alt="" width="220"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
        </div>

        <div>

        </div>

        <div>
            <div>
                <span style="font-size: 13px;">Property:   @feature</span>
            </div>
        </div>

        <div>
            <div>
                <span style="font-size: 8px;">@index <br>@p_xyzs <br>@p_images <br></span>
            </div>
        </div>


        """

tooltips['atomic'] = """
    <div>
            <img
                src="@p_images" height="220" alt="" width="220"
                style="float: left; margin: 0px 15px 15px 0px;"
                border="2"
            ></img>
    </div>


    <div>
        <div>
            <span style="font-size: 13px;">Property:   @feature</span>
        </div>
    </div>

    <div>
            <span style="font-size: 13px;">Atomid:   @atomic_num</span>
    </div>

    <div>
        <div>
            <span style="font-size: 8px;">@index <br>@p_xyzs <br>@p_images <br></span>
        </div>
    </div>


    """

tooltips['generic'] = """
        <div>
            <div>
                <span style="font-size: 13px;">Property:   @feature</span>
            </div>
        </div>

        <div>
            <div>
                <span style="font-size: 8px;">@index <br>@p_xyzs</span>
            </div>
        </div>


        """
