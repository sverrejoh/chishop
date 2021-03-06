""" models.py

Copyright (c) 2009, Ask Solem
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

Neither the name of Ask Solem nor the names of its contributors may be used
to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

"""

import os
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

OS_NAMES = (
        ("aix", "AIX"),
        ("beos", "BeOS"),
        ("debian", "Debian Linux"),
        ("dos", "DOS"),
        ("freebsd", "FreeBSD"),
        ("hpux", "HP/UX"),
        ("mac", "Mac System x."),
        ("macos", "MacOS X"),
        ("mandrake", "Mandrake Linux"),
        ("netbsd", "NetBSD"),
        ("openbsd", "OpenBSD"),
        ("qnx", "QNX"),
        ("redhat", "RedHat Linux"),
        ("solaris", "SUN Solaris"),
        ("suse", "SuSE Linux"),
        ("yellowdog", "Yellow Dog Linux"),
)

ARCHITECTURES = (
    ("alpha", "Alpha"),
    ("hppa", "HPPA"),
    ("ix86", "Intel"),
    ("powerpc", "PowerPC"),
    ("sparc", "Sparc"),
    ("ultrasparc", "UltraSparc"),
)

UPLOAD_TO = getattr(settings,
    "DJANGOPYPI_RELEASE_UPLOAD_TO", 'dist')

class Classifier(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = _(u"classifier")
        verbose_name_plural = _(u"classifiers")

    def __unicode__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    license = models.TextField(blank=True)
    metadata_version = models.CharField(max_length=64, default=1.0)
    author = models.CharField(max_length=128, blank=True)
    home_page = models.URLField(verify_exists=False, blank=True, null=True)
    download_url = models.URLField(verify_exists=False, blank=True, null=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    author_email = models.CharField(max_length=255, blank=True)
    classifiers = models.ManyToManyField(Classifier)
    owner = models.ForeignKey(User, related_name="projects")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _(u"project")
        verbose_name_plural = _(u"projects")

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('djangopypi-show_links', (), {'dist_name': self.name})

    @models.permalink
    def get_pypi_absolute_url(self):
        return ('djangopypi-pypi_show_links', (), {'dist_name': self.name})

    def get_release(self, version):
        """Return the release object for version, or None"""
        try:
            return self.releases.get(version=version)
        except Release.DoesNotExist:
            return None

class Release(models.Model):
    version = models.CharField(max_length=128)
    distribution = models.FileField(upload_to=UPLOAD_TO)
    md5_digest = models.CharField(max_length=255, blank=True)
    platform = models.CharField(max_length=255, blank=True)
    signature = models.CharField(max_length=128, blank=True)
    filetype = models.CharField(max_length=255, blank=True)
    pyversion = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey(Project, related_name="releases")
    upload_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _(u"release")
        verbose_name_plural = _(u"releases")
        unique_together = ("project", "version")

    def __unicode__(self):
        return u"%s (%s)" % (self.release_name, self.platform)

    @property
    def type(self):
        dist_file_types = {
            'sdist':'Source',
            'bdist_dumb':'"dumb" binary',
            'bdist_rpm':'RPM',
            'bdist_wininst':'MS Windows installer',
            'bdist_egg':'Python Egg',
            'bdist_dmg':'OS X Disk Image'}
        return dist_file_types.get(self.filetype, self.filetype)

    @property
    def filename(self):
        return os.path.basename(self.distribution.name)

    @property
    def release_name(self):
        return u"%s-%s" % (self.project.name, self.version)

    @property
    def path(self):
        return self.distribution.name

    @models.permalink
    def get_absolute_url(self):
        return ('djangopypi-show_version', (), {'dist_name': self.project, 'version': self.version})

    def get_dl_url(self):
        return "%s#md5=%s" % (self.distribution.url, self.md5_digest)
