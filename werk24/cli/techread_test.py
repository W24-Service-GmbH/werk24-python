
import argparse
import mock
import aiounittest
from werk24.cli.techread import main
from werk24.models.ask import W24AskType
from dotenv import load_dotenv

load_dotenv(".werk24")


class TechreadTest(aiounittest.AsyncTestCase):
    """ Small Test Case ensuring that the CLI associating
    interface does not change.
    """

    def _make_args(self):
        """ Make the args, requesting all asks
        """
        # mock the arguments
        args = argparse.Namespace()
        args.input_file = "."
        args.ignore_architecture_status = True
        args.ask_techread_started = True
        args.ask_page_thumbnail = True
        args.ask_sheet_thumbnail = True
        args.ask_sectional_thumbnail = True
        args.ask_variant_overall_dimensions = True
        args.ask_train = True
        return args

    @mock.patch('werk24.techread_client.W24TechreadClient')
    @mock.patch('werk24.cli.techread._get_drawing')
    async def test_ask_techread_started(
            self,
            get_drawing_mock,
            ClientMock):
        """ Test whether the cli-arguments translate into the
        correct W24AskTypes on the Hooks.
        """

        # mock the get_drawing function
        get_drawing_mock.return_value = ""

        # mock the args
        args = self._make_args()

        # call cli module
        await main(args)

        # get the list of Hooks
        client = ClientMock()
        async with client as session:
            hooks = session.read_drawing_with_hooks.call_args[0][1]
            ask_types = [h.ask.ask_type for h in hooks if h.ask is not None]

        # and compare
        assert W24AskType.PAGE_THUMBNAIL in ask_types
        assert W24AskType.SHEET_THUMBNAIL in ask_types
        assert W24AskType.SECTIONAL_THUMBNAIL in ask_types
        assert W24AskType.TRAIN in ask_types
