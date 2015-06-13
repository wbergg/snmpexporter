import abc
import collections


AnnotatedResultEntry = collections.namedtuple('AnnotatedResultEntry',
    ('data', 'mib', 'obj', 'index', 'interface', 'vlan'))

Statistics = collections.namedtuple('Statistics', ('timeouts', 'errors'))


class Action(object):
  """Base class that represents an Action that moves between stages."""
  __metadata__ = abc.ABCMeta

  @classmethod
  def get_queue(cls, instance):
    return 'dhmon:snmp:{0}:{1}'.format(instance, cls.__name__)

  @abc.abstractmethod
  def do(self, stage):
    """Execute an action, return a list of result actions."""
    pass


class Trigger(Action):
  """Trigger the supervisor to start a new poll."""

  def do(self, stage):
    return stage.do_trigger()


class SnmpWalk(Action):
  """Walk over a given device."""

  def __init__(self, target):
    self.target = target

  def do(self, stage):
    return stage.do_snmp_walk(self.target)


class Summary(Action):
  """Summary for this poll round.

  Used to calculate when a round is over to get queue statistics.
  """

  def __init__(self, timestamp, targets):
    """
    Args:
      timestamp: (float) unix timestamp used to group targets in the round.
      targets: (int) number of targets in this round.
    """
    self.timestamp = timestamp
    self.targets = targets

  def do(self, stage):
    return stage.do_summary(timestamp, targets)


class Result(Action):
  """One target's Exporter set."""

  def __init__(self, target, results, stats):
    self.target = target
    self.results = results
    self.stats = stats

  def do(self, stage):
    return stage.do_result(self.target, self.results, self.stats)


class AnnotatedResult(Result):
  """Same as Result but now the data is annotated."""
  pass