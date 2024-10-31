import unittest
from pathlib import Path

from pip._internal.req.req_file import parse_requirements
from pip._internal.req.constructors import install_req_from_parsed_requirement
from pip._internal.network.session import PipSession
from pip._internal.exceptions import DistributionNotFound

_REQUIREMENTS_PATH = Path( __file__ ).parent.with_name( 'requirements.txt' )

class TestRequirements( unittest.TestCase ):
    """Test availability of required packages."""

    def test_requirements( self ):
        """Test that each required package is available."""

        session = PipSession()
        requirements = parse_requirements( str( _REQUIREMENTS_PATH ), session )

        for requirement in requirements:
            req_to_install = install_req_from_parsed_requirement( requirement )
            req_to_install.check_if_exists( use_user_site=False )
            with self.subTest( req_to_install=str( req_to_install ) ):
                if not req_to_install.satisfied_by:
                    raise DistributionNotFound()

if __name__ == '__main__':
    unittest.main()