import unittest

from unittest.mock import MagicMock

from pluginsmanager.model.lv2.lv2_effect_builder import Lv2EffectBuilder
from pluginsmanager.model.pedalboard import Pedalboard

from pluginsmanager.model.update_type import UpdateType
from pluginsmanager.model.system.system_effect import SystemEffect

from pluginsmanager.model.connection import ConnectionError


class OutputTest(unittest.TestCase):
    builder = None

    @classmethod
    def setUpClass(cls):
        cls.builder = Lv2EffectBuilder()

    def test_connect(self):
        pedalboard = Pedalboard('Pedalboard name')
        pedalboard.observer = MagicMock()

        builder = OutputTest.builder
        reverb = builder.build('http://calf.sourceforge.net/plugins/Reverb')
        reverb2 = builder.build('http://calf.sourceforge.net/plugins/Reverb')

        pedalboard.append(reverb)
        pedalboard.append(reverb2)

        self.assertEqual(0, len(pedalboard.connections))
        reverb.outputs[0].connect(reverb2.inputs[0])
        self.assertEqual(1, len(pedalboard.connections))

        new_connection = pedalboard.connections[0]
        pedalboard.observer.on_connection_updated.assert_called_with(
            new_connection,
            UpdateType.CREATED,
            index=len(pedalboard.connections) - 1,
            origin=pedalboard
        )

        reverb.outputs[1].connect(reverb2.inputs[1])
        self.assertEqual(2, len(pedalboard.connections))

        new_connection = pedalboard.connections[-1]
        pedalboard.observer.on_connection_updated.assert_called_with(
            new_connection,
            UpdateType.CREATED,
            index=len(pedalboard.connections) - 1,
            origin=pedalboard
        )

    def test_disconnect(self):
        pedalboard = Pedalboard('Pedalboard name')

        builder = OutputTest.builder
        reverb = builder.build('http://calf.sourceforge.net/plugins/Reverb')
        reverb2 = builder.build('http://calf.sourceforge.net/plugins/Reverb')

        pedalboard.append(reverb)
        pedalboard.append(reverb2)

        reverb.outputs[0].connect(reverb2.inputs[0])
        reverb.outputs[1].connect(reverb2.inputs[0])
        self.assertEqual(2, len(pedalboard.connections))

        pedalboard.observer = MagicMock()

        disconnected = pedalboard.connections[-1]
        reverb.outputs[1].disconnect(reverb2.inputs[0])
        self.assertEqual(1, len(pedalboard.connections))
        pedalboard.observer.on_connection_updated.assert_called_with(
            disconnected,
            UpdateType.DELETED,
            index=len(pedalboard.connections),
            origin=pedalboard
        )

        disconnected = pedalboard.connections[-1]
        reverb.outputs[0].disconnect(reverb2.inputs[0])
        self.assertEqual(0, len(pedalboard.connections))
        pedalboard.observer.on_connection_updated.assert_called_with(
            disconnected,
            UpdateType.DELETED,
            index=len(pedalboard.connections),
            origin=pedalboard
        )

    def test_disconnect_connection_not_created(self):
        pedalboard = Pedalboard('Pedalboard name')

        builder = OutputTest.builder
        reverb = builder.build('http://calf.sourceforge.net/plugins/Reverb')
        reverb2 = builder.build('http://calf.sourceforge.net/plugins/Reverb')

        pedalboard.append(reverb)
        pedalboard.append(reverb2)

        pedalboard.observer = MagicMock()

        with self.assertRaises(ValueError):
            reverb.outputs[1].disconnect(reverb2.inputs[0])

        pedalboard.observer.on_connection_updated.assert_not_called()

    def test_connect_system_effect(self):
        sys_effect = SystemEffect('system', ['capture_1'], ['playback_1', 'playback_2'])

        effect_output = sys_effect.outputs[0]
        effect_input = sys_effect.inputs[0]

        with self.assertRaises(ConnectionError):
            effect_output.connect(effect_input)

    def test_disconnect_system_effect(self):
        sys_effect = SystemEffect('system', ['capture_1'], ['playback_1', 'playback_2'])

        effect_output = sys_effect.outputs[0]
        effect_input = sys_effect.inputs[0]

        with self.assertRaises(ConnectionError):
            effect_output.disconnect(effect_input)
