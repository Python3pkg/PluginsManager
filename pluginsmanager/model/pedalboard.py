from pluginsmanager.util.observable_list import ObservableList
from pluginsmanager.model.update_type import UpdateType

from unittest.mock import MagicMock


class Pedalboard(object):
    """
    Pedalboard is a patch representation: your structure contains
    :class:`Effect` and :class:`Connection`::

        >>> pedalboard = Pedalboard('Rocksmith')
        >>> bank.append(pedalboard)

        >>> builder = Lv2EffectBuilder()
        >>> pedalboard.effects
        ObservableList: []
        >>> reverb = builder.build('http://calf.sourceforge.net/plugins/Reverb')
        >>> pedalboard.append(reverb)
        >>> pedalboard.effects
        ObservableList: [<Lv2Effect object as 'Calf Reverb'  active at 0x7f60effb09e8>]

        >>> fuzz = builder.build('http://guitarix.sourceforge.net/plugins/gx_fuzzfacefm_#_fuzzfacefm_')
        >>> pedalboard.effects.append(fuzz)

        >>> pedalboard.connections
        ObservableList: []
        >>> pedalboard.connections.append(Connection(sys_effect.outputs[0], fuzz.inputs[0])) # View SystemEffect for more details
        >>> pedalboard.connections.append(Connection(fuzz.outputs[0], reverb.inputs[0]))
        >>> # It works too
        >>> reverb.outputs[1].connect(sys_effect.inputs[0])
        ObservableList: [<Connection object as 'system.capture_1 -> GxFuzzFaceFullerMod.In' at 0x7f60f45f3f60>, <Connection object as 'GxFuzzFaceFullerMod.Out -> Calf Reverb.In L' at 0x7f60f45f57f0>, <Connection object as 'Calf Reverb.Out R -> system.playback_1' at 0x7f60f45dacc0>]

    For load the pedalboard for play the songs with it::

        >>> mod_host.pedalboard = pedalboard

    All changes in the pedalboard will be reproduced in mod-host

    :param string name: Pedalboard name
    """
    def __init__(self, name):
        self.name = name
        self._effects = ObservableList()
        self._connections = ObservableList()

        self.effects.observer = self._effects_observer
        self.connections.observer = self._connections_observer

        self._observer = MagicMock()

        self.bank = None

    @property
    def observer(self):
        return self._observer

    @observer.setter
    def observer(self, observer):
        self._observer = observer

        for effect in self.effects:
            effect.observer = observer

    def _effects_observer(self, update_type, effect, index):
        kwargs = {
            'index': index,
            'origin': self
        }

        if update_type == UpdateType.CREATED \
        or update_type == UpdateType.UPDATED:
            effect.pedalboard = self
            effect.observer = self.observer
        elif update_type == UpdateType.DELETED:
            for connection in effect.connections:
                self.connections.remove(connection)

            effect.pedalboard = None
            effect.observer = MagicMock()

        self.observer.on_effect_updated(effect, update_type, **kwargs)

    def _connections_observer(self, update_type, connection, index):
        self.observer.on_connection_updated(connection, update_type)

    @property
    def json(self):
        """
        Get a json decodable representation of this pedalboard

        :return dict: json representation
        """
        return self.__dict__

    @property
    def __dict__(self):
        return {
            'name': self.name,
            'effects': [effect.json for effect in self.effects],
            'connections': [connection.json for connection in self.connections]
        }

    def append(self, effect):
        """
        Add a :class:`Effect` in this pedalboard

        This works same as::

            >>> pedalboard.effects.append(effect)

        or::

            >>> pedalboard.effects.insert(len(pedalboard.effects), effect)

        :param Effect effect: Effect that will be added
        """
        self.effects.append(effect)

    @property
    def effects(self):
        """
        Return the effects presents in the pedalboard

        .. note::

            Because the effects is an :class:`ObservableList`, it isn't settable.
            For replace, del the effects unnecessary and add the necessary
            effects
        """
        return self._effects

    @property
    def connections(self):
        """
        Return the pedalboard connections list

        .. note::

            Because the connections is an :class:`ObservableList`, it isn't settable.
            For replace, del the connections unnecessary and add the necessary
            connections
        """
        return self._connections