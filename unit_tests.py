#!/usr/bin/python
# pylint: disable=E1103,E1101
#
# unit test
import shutil

import sys
import os
import tempfile
from string import Template
from mock import patch
import datetime
try:
    import unittest2
except:
    import unittest as unittest2

from mail_validator import *


class TestHelper():
    def generate_Test_Message(recipient='test_recipient@unittest.invalid',
                              sender='test_sender@unittest.invalid',
                              messageid='20140410142742.2721.35604@unittest.invalid',
                              selector=datetime.now().strftime('%Y%m%d%H%M%S'),
                              dkim=False,
                              tls=False):
        mailtemplate = Template("""
Return-Path: <$recipient>
X-Original-To: $recipient
Delivered-To: $recipient
Received: from unittest.invalid (unittest.invalid [1.2.3.4])
    $tlssignatur
    (No client certificate requested)
    by unittest.invalid (Postfix) with ESMTPS id A7E9D60039
    for <$recipient>; Thu, 10 Apr 2014 16:27:42 +0200 (CEST)
Received: from mailer (localhost [127.0.0.1])     by unittest.invalid (Postfix) with ESMTP id 8F5DD274F
    for <$recipient>; Thu, 10 Apr 2014 16:27:42 +0200 (CEST)$dkimsignatur
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: test mail from mail_validator.py[unittest.invalid]
Date: Thu, 10 Apr 2014 16:27:42 +0200
From: $sender
X-CSA-Complaints: whitelist-complaints@eco.de
To: $recipient
Message-ID: <$messageid>

This is a autogenerated message for mail verification tests
""")
        dkimsignaturtemplate = Template("""
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
    d=unittest.invalid; s=$selector; t=1397140062;
    bh=yO9ahVUXamt9uV06AyxfBXhhy202+cmz8IM4gKl9O3Q=;
    h=Subject:Date:From:To;
    b=ASnU4pnVLWehDEv8kKDsSrOUucCt2GNNl7PPxGYCULR1tz3kPz/C9kBf2fnO2OY1m
     syAEkzDJoVS4BLuT5oJp2Mjsg2u82Jubck7JF2roWe1eGWAgJCSOuaTE+v65DOMiwm
     lWm1GZ0oY6iuXTkkUMQ8tqqclX7fGtpBs59MK0juvchBiyGmZPodTDuNyORQn2ukX0
     ucGs+3Yld2EiwGtDQZA5OHKo03pynf4J1hBMAtkEddOTKk/er0zr2VBeA5d2GYJpvM
     QyLtrFlltgHegm8bO5YvXH7VJaquNY+om/txD2eBwpZMObhqh8DaAzXzGUgwbuuuaS
     LX9ALJM+lYq2g==)""")

        dkimsignatur = dkimsignaturtemplate.substitute(selector=selector) if dkim else ''
        tlssignatur = '(using TLSv1.2 with cipher DHE-RSA-AES256-GCM-SHA384 (256/256 bits))' if tls else ''

        return mailtemplate.substitute(recipient=recipient,
                                       sender=sender,
                                       messageid=messageid,
                                       dkimsignatur=dkimsignatur,
                                       tlssignatur=tlssignatur)

    def options(self):
        self.smtp_host = 'localhost'
        self.smtp_port = 25
        self.imap_host = 'localhost'
        self.user = 'user'
        self.password = 'password'
        self.mailbox = 'catchall'
        self.sender = 'tester@test.invalid'
        self.to = 'tester@test.invalid'
        self.output = None
        self.validate = 'dkim'

        return self


class MainUnitTestCase(unittest2.TestCase):
    def setUp(self):
        self.options = TestHelper().options()
        self.tempdir = tempfile.mkdtemp()

        #Setup SMTP
        self.smtp = SmtpSender(self.options)

        # Setup IMAP
        self.imap = ImapReceiver(self.options.imap_host, self.options.user, self.options.password, self.options.mailbox)

        # Setup Validator
        self.mail_validator = Validator()

    def tearDown(self):
        if self.tempdir and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    # SMTP Tests
    @patch('mail_validator.smtplib.SMTP')
    def test_should_connect_to_correct_smtp(self, patchsmtplib):
        return_code, content = self.smtp.connect()
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertEqual(content, '', "Message should be empty")

    @patch('socket.gethostname')
    def test_should_output_correct_mail(self, patchgethostname):
        patchgethostname.return_value = 'unittesthost.invalid'
        body = self.smtp.compose_mail()
        self.assertEqual(body['To'], self.options.to, "Recipient should be equal")
        self.assertEqual(body['From'], self.options.sender, "Sender should be equal")

    @patch('mail_validator.smtplib.SMTP')
    @patch('socket.gethostname')
    def test_should_send_test_mail(self, patchgethostname, patchsmtplib):
        patchgethostname.return_value = 'unittesthost.invalid'
        self.smtp.connect()
        return_code, message_id = self.smtp.send_test_mail()
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertTrue("@unittesthost.invalid" in message_id, "Correct Message Id should be returned")

    # IMAP Tests
    @patch('mail_validator.imaplib.IMAP4')
    def test_should_connect_to_imap(self, patchimaplib):
        return_code, content = self.imap.connect()
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertEqual(content, '', "Message should be empty")

    @patch('mail_validator.imaplib.IMAP4')
    def test_should_get_test_message(self, patchimaplib):
        patchimaplib.return_value.search.return_value = (0, [6])

        # This is a multidomainarray example returned by imaplib.IMAP4.fetch
        IMAP_FETCH_DATA = ['313 (FLAGS (\\Seen \\Recent))', [('312 (FLAGS (\\Seen \\Recent) RFC822 {1688}', 'Return-Path: <test_recipient@unittest.invalid>\r\nX-Original-To: test_recipient@unittest.invalid\r\nDelivered-To: test_recipient@unittest.invalid\r\nReceived: from unittest.invalid (unittest.invalid.is [1.2.3.4])\r\n\t(using TLSv1.2 with cipher DHE-RSA-AES256-GCM-SHA384 (256/256 bits))\r\n\t(No client certificate requested)\r\n\tby unittest.invalid (Postfix) with ESMTPS id A7E9D60039\r\n\tfor <test_recipient@unittest.invalid>; Thu, 10 Apr 2014 16:27:42 +0200 (CEST)\r\nReceived: from mailer (localhost [127.0.0.1]) \tby unittest.invalid (Postfix) with ESMTP id 8F5DD274F\r\n\tfor <test_recipient@unittest.invalid>; Thu, 10 Apr 2014 16:27:42 +0200 (CEST)\r\nContent-Type: text/plain; charset="us-ascii"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: 7bit\r\nSubject: tls test mail from mail_validator.py[unittest.invalid]\r\nDate: Thu, 10 Apr 2014 16:27:42 +0200\r\nFrom: test_recipient@unittest.invalid\r\nX-CSA-Complaints: whitelist-complaints@eco.de\r\nTo: test_recipient@unittest.invalid\r\nMessage-ID: <20140410142742.2721.35604@unittest.invalid>\r\n\r\nThis is a autogenerated message for mail verification tests\r\n')]]
        (typ, data) = IMAP_FETCH_DATA
        patchimaplib.return_value.fetch.return_value = IMAP_FETCH_DATA
        message_id = '20140410090245.28014.85408@unittesthost.invalid'
        self.imap.connect()
        return_code, mail = self.imap.get_test_message(message_id)
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertEqual(mail, data[0][1], "Message should be empty")

    #Validator
    @patch('mail_validator.dkim.verify')
    def test_should_validate_correct_message_with_dkim(self, patchdkimverify):
        patchdkimverify.return_value = True
        selector = datetime.now().strftime('%Y%m%d%H%M%S')
        mail = TestHelper().generate_Test_Message(dkim=True, sender='test_recipient@unittest.invalid', selector=selector)
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertEqual(message, 'DKIM verification successful, selector is %s' % selector, "Message should be correct")

    @patch('mail_validator.dkim.verify')
    def test_should_not_validate_message_with_old_dkim_selector(self, patchdkimverify):
        patchdkimverify.return_value = True
        mail = TestHelper().generate_Test_Message(dkim=True, selector='20120101101010')
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 2, "Returncode should be 2")
        self.assertTrue('DKIM key older than' in message, "Message contain a hint to the old key")

    @patch('mail_validator.dkim.verify')
    def test_should_not_validate_incorrect_message_with_dkim(self, patchdkimverify):
        patchdkimverify.return_value = False
        mail = TestHelper().generate_Test_Message(dkim=True)
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 2, "Returncode should be 2")
        self.assertEqual(message, 'DKIM verification failed', "Message should be correct")

    def test_should_not_validate_correct_message_without_dkim(self):
        mail = TestHelper().generate_Test_Message()
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 2, "Returncode should be 2")
        self.assertEqual(message, 'No dkim signature found', "Message should be correct")

    def test_should_validate_correct_message_with_tls(self):
        self.options.validate = 'tls'
        mail = TestHelper().generate_Test_Message(tls=True)
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 0, "Returncode should be 0")
        self.assertTrue('TLS verification successful, mail was sent' in message, "Message should contain a hint to the TLS Transport")

    def test_should_not_validate_correct_message_without_tls(self):
        self.options.validate = 'tls'
        mail = TestHelper().generate_Test_Message()
        return_code, message = self.mail_validator.validate_message(mail, self.options, self.options.output)
        self.assertEqual(return_code, 2, "Returncode should be 2")
        self.assertEqual('No TLS log found', message, "Message should contain a hint to the missing TLS Transport")

if __name__ == "__main__":
    runner = None
    try:
        if os.getenv("TEAMCITY_PROJECT_NAME") is not None:
            from teamcity.unittestpy import TeamcityTestRunner
            runner = TeamcityTestRunner()
    except:
        print >> sys.stderr, "WARNING: Could not import teamcity.unittestpy, install it and enjoy better Teamcity integration"

    unittest2.main(testRunner=runner)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
