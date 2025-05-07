import json
import Data_Scientist.yaml
import xml.etree.ElementTree as ET
import hashlib

class SerializerError(Exception):
    """Custom exception for serialization errors."""
    pass

class DataTransformer:
    """
    A class to serialize and deserialize data across multiple formats,
    check data integrity, and support nested structures.
    """
    SUPPORTED_FORMATS = ['json', 'yaml', 'xml']

    def serialize(self, data, fmt):
        """
        Serialize Python data to the specified format.
        Supported formats: 'json', 'yaml', 'xml'.
        Returns a string representation.
        """
        if fmt == 'json':
            return json.dumps(data)
        elif fmt == 'yaml':
            return yaml.dump(data)
        elif fmt == 'xml':
            root = ET.Element('root')
            self._dict_to_xml(data, root)
            return ET.tostring(root, encoding='utf-8').decode('utf-8')
        else:
            raise SerializerError(f'Unsupported format: {fmt}')

    def deserialize(self, serialized_str, fmt):
        """
        Deserialize a string in the specified format to Python data.
        Supported formats: 'json', 'yaml', 'xml'.
        """
        if fmt == 'json':
            return json.loads(serialized_str)
        elif fmt == 'yaml':
            return yaml.safe_load(serialized_str)
        elif fmt == 'xml':
            root = ET.fromstring(serialized_str)
            return self._xml_to_dict(root)
        else:
            raise SerializerError(f'Unsupported format: {fmt}')

    def cross_language_support(self, data, fmt):
        """
        Serialize and then deserialize the data in the given format.
        Returns a tuple: (serialized_str, deserialized_data, success_flag)
        """
        serialized = self.serialize(data, fmt)
        deserialized = self.deserialize(serialized, fmt)
        success = deserialized == data
        return serialized, deserialized, success

    def data_integrity_checks(self, data):
        """
        For each supported format, serialize the data, compute a SHA256 checksum,
        and verify round-trip integrity.
        Returns a dict mapping format to {'checksum': str, 'round_trip': bool}.
        """
        results = {}
        for fmt in self.SUPPORTED_FORMATS:
            serialized = self.serialize(data, fmt)
            checksum = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
            _, _, success = self.cross_language_support(data, fmt)
            results[fmt] = {
                'checksum': checksum,
                'round_trip': success
            }
        return results

    def nested_structures(self, data):
        """
        Ensure that nested data structures can be serialized/deserialized
        in all supported formats. Delegates to data_integrity_checks.
        """
        return self.data_integrity_checks(data)

    def unit_testing(self):
        """
        Placeholder for unit testing instruction.
        """
        return 'Run pytest to execute unit tests.'

    def _dict_to_xml(self, data, parent):
        """
        Recursively build XML elements from Python dict/list/primitive.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(parent, key)
                self._dict_to_xml(value, elem)
        elif isinstance(data, list):
            for item in data:
                item_elem = ET.SubElement(parent, 'item')
                self._dict_to_xml(item, item_elem)
        else:
            parent.text = str(data)

    def _xml_to_dict(self, elem):
        """
        Recursively convert an XML element (and children) back to Python data.
        """
        children = list(elem)
        if not children:
            # Leaf node
            return self._convert_text(elem.text)
        # If all children are <item>, treat as list
        if all(child.tag == 'item' for child in children):
            return [self._xml_to_dict(child) for child in children]
        # Otherwise, dict
        result = {}
        for child in children:
            result[child.tag] = self._xml_to_dict(child)
        return result

    def _convert_text(self, text):
        """
        Attempt to convert text to int, float, bool, or leave as string.
        """
        if text is None:
            return None
        t = text.strip()
        if t.lower() in ('true', 'false'):
            return t.lower() == 'true'
        try:
            return int(t)
        except ValueError:
            pass
        try:
            return float(t)
        except ValueError:
            pass
        return t
