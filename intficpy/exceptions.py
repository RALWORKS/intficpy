class Unserializable(Exception):
    """
    The item is not serializable by the save system.
    """

    pass


class DeserializationError(Exception):
    """
    Error deserializing a value during game load
    """

    pass


class VerbDefinitionError(Exception):
    """
    A verb is defined in an incorrect or inconsistent way
    """

    pass


class ParserError(Exception):
    """
    Error parsing the player command
    """

    pass


class VerbMatchError(ParserError):
    """
    No matching verb could be identified from the player input
    """

    pass


class ObjectMatchError(ParserError):
    """
    No matching IFPObject could be found for either the direct or indirect object
    in the player command
    """

    pass


class OutOfRange(ParserError):
    """
    The specified object is out of range for the current verb
    """

    pass


class AbortTurn(Exception):
    """
    Abort the current turn. Error message will not be printed.
    """

    pass


class NoMatchingSuggestion(Exception):
    def __init__(self, query, options, matches):
        self.query = query
        self.options = options
        self.matches = matches

        msg = (
            f"Unable to unambiguaously match a suggestion from options {options} "
            f"with query `{query}`. Not excluded: {matches}."
        )
        super().__init__(msg)


class IFPError(Exception):
    pass
