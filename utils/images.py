import logging
import os
import requests
import shutil

from mtgcardbox.models import CardEdition

logger = logging.getLogger(__name__)


class MCIDownloader:
    """Download images from magiccards.info."""
    URL = 'http://magiccards.info/scans/en'

    @staticmethod
    # TODO(benedikt) log information
    def get_card_edition_image(edition, outfile):
        """Download a single card image."""
        image_url = '{0}/{1}/{2}.jpg'.format(MCIDownloader.URL,
                                             edition.mtgset.code.lower(),
                                             str(edition.number) +
                                             edition.number_suffix)
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            with open(outfile, 'wb') as image:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, image)
                logger.info("New image for '{0}'.".format(edition))
        else:
            logger.warning("No image for '{0}' at '{1}'.".format(edition,
                                                                 image_url))

    @staticmethod
    def get_card_edition_images(outdir):
        """Download card images for all cards in the database."""
        editions = CardEdition.objects.all().select_related('mtgset')
        for edition in editions:
            image_dir = os.path.join(outdir, edition.mtgset.code)
            image_name = str(edition.number) + edition.number_suffix + '.jpg'
            os.makedirs(image_dir, exist_ok=True)
            MCIDownloader.get_card_edition_image(
                edition, os.path.join(image_dir, image_name))
