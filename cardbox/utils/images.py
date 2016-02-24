# django-cardbox -- A collection manager for Magic: The Gathering
# Copyright (C) 2016 Benedikt Rascher-Friesenhausen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import os
import requests
import shutil

from cardbox.models import CardEdition

logger = logging.getLogger(__name__)


class MCIDownloader:
    """Download images from magiccards.info."""
    URL = 'http://magiccards.info/scans/en'

    @staticmethod
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
