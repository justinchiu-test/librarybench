import unittest
import os
import json
from package_manager import PackageManager, VersionConflictError


class TestPackageManagerV1(unittest.TestCase):
    def setUp(self):
        self.pm = PackageManager()

    def test_install_package_without_dependencies(self):
        self.pm.install_package_v1("A", [])
        self.assertTrue(self.pm.is_installed("A"))
        self.assertEqual(self.pm.list_packages_v1(), ["A"])

    def test_install_package_with_dependencies(self):
        self.pm.install_package_v1("A", ["B", "C"])
        self.pm.install_package_v1("B", ["D"])
        self.pm.install_package_v1("C", [])
        self.pm.install_package_v1("D", [])
        
        self.assertTrue(self.pm.is_installed("A"))
        self.assertTrue(self.pm.is_installed("B"))
        self.assertTrue(self.pm.is_installed("C"))
        self.assertTrue(self.pm.is_installed("D"))
        
        # Order may vary, so we sort before comparing
        self.assertEqual(sorted(self.pm.list_packages_v1()), ["A", "B", "C", "D"])

    def test_install_package_recursive_dependencies(self):
        self.pm.install_package_v1("X", ["Y"])
        self.pm.install_package_v1("Y", ["Z"])
        self.pm.install_package_v1("Z", [])
        
        all_installed = self.pm.list_packages_v1()
        self.assertEqual(sorted(all_installed), ["X", "Y", "Z"])

    def test_remove_package_not_dependency(self):
        self.pm.install_package_v1("A", [])
        self.assertTrue(self.pm.is_installed("A"))
        
        self.pm.remove_package("A")
        self.assertFalse(self.pm.is_installed("A"))
        self.assertEqual(self.pm.list_packages_v1(), [])

    def test_remove_package_is_dependency(self):
        self.pm.install_package_v1("A", ["B"])
        self.pm.install_package_v1("B", [])
        
        with self.assertRaises(Exception):
            self.pm.remove_package("B")
            
        self.assertTrue(self.pm.is_installed("B"))

    def test_remove_package_after_parent_removed(self):
        self.pm.install_package_v1("A", ["B"])
        self.pm.install_package_v1("B", [])
        
        self.pm.remove_package("A")
        self.pm.remove_package("B")  # Should work now that A is gone
        
        self.assertFalse(self.pm.is_installed("A"))
        self.assertFalse(self.pm.is_installed("B"))
        self.assertEqual(self.pm.list_packages_v1(), [])

    def test_is_installed(self):
        self.assertFalse(self.pm.is_installed("NonExistent"))
        
        self.pm.install_package_v1("Test", [])
        self.assertTrue(self.pm.is_installed("Test"))

    def test_list_packages_empty(self):
        self.assertEqual(self.pm.list_packages_v1(), [])

    def test_install_existing_package(self):
        self.pm.install_package_v1("A", [])
        # Installing again should be fine
        self.pm.install_package_v1("A", [])
        self.assertEqual(self.pm.list_packages_v1(), ["A"])

    def test_circular_dependency(self):
        # Setup a circular dependency A->B->C->A
        self.pm.install_package_v1("A", ["B"])
        self.pm.install_package_v1("B", ["C"])
        
        # This should detect the circular dependency
        with self.assertRaises(Exception):
            self.pm.install_package_v1("C", ["A"])


class TestPackageManagerV2(unittest.TestCase):
    def setUp(self):
        self.pm = PackageManager()
        self._cleanup_test_files()

    def tearDown(self):
        self._cleanup_test_files()

    def _cleanup_test_files(self):
        """Remove any test lockfiles and environments"""
        if os.path.exists("lock.json"):
            os.remove("lock.json")
        if os.path.exists("test.lock.json"):
            os.remove("test.lock.json")
        
        # Clean up test environments
        if os.path.exists("test_env"):
            import shutil
            shutil.rmtree("test_env", ignore_errors=True)
        if os.path.exists("dev_env"):
            import shutil
            shutil.rmtree("dev_env", ignore_errors=True)

    def test_version_support(self):
        """Test that packages can be installed with specific versions"""
        self.pm.install_package("A", "1.0", [])
        self.pm.install_package("A", "2.0", [])
        self.pm.install_package("B", "1.5", ["A>=1.0"])
        
        self.assertTrue(self.pm.is_installed("A", "1.0"))
        self.assertTrue(self.pm.is_installed("A", "2.0"))
        self.assertTrue(self.pm.is_installed("B", "1.5"))

    def test_version_constraint_solver(self):
        """Test that the dependency solver can resolve appropriate versions"""
        # Add multiple versions to the registry
        self.pm.add_to_registry("A", "1.0", [])
        self.pm.add_to_registry("A", "1.5", [])
        self.pm.add_to_registry("A", "2.0", [])
        self.pm.add_to_registry("A", "3.0", [])
        self.pm.add_to_registry("B", "1.0", ["A>=1.0,<3.0"])
        
        # Install with constraints
        self.pm.install("B==1.0")
        
        # Should pick A 2.0 as it's the latest within the constraint
        self.assertTrue(self.pm.is_installed("A", "2.0"))
        self.assertFalse(self.pm.is_installed("A", "3.0"))  # This would be out of constraint

    def test_version_conflict(self):
        """Test that version conflicts are properly detected"""
        self.pm.add_to_registry("A", "1.0", [])
        self.pm.add_to_registry("A", "2.0", [])
        self.pm.add_to_registry("B", "1.0", ["A==1.0"])
        self.pm.add_to_registry("C", "1.0", ["A==2.0"])
        
        # Install the first package
        self.pm.install("B==1.0")
        
        # This should raise a version conflict error
        with self.assertRaises(VersionConflictError):
            self.pm.install("C==1.0")

    def test_virtual_environments(self):
        """Test creating and using virtual environments"""
        # Create environments
        self.pm.create_env("test_env")
        self.pm.create_env("dev_env")
        
        # Install packages in test_env
        self.pm.use_env("test_env")
        self.pm.install_package("A", "1.0", [])
        self.assertTrue(self.pm.is_installed("A", "1.0"))
        
        # Switch to dev_env and verify A is not installed
        self.pm.use_env("dev_env")
        self.assertFalse(self.pm.is_installed("A", "1.0"))
        
        # Install different package in dev_env
        self.pm.install_package("B", "2.0", [])
        self.assertTrue(self.pm.is_installed("B", "2.0"))
        
        # Switch back to test_env and verify B is not installed
        self.pm.use_env("test_env")
        self.assertTrue(self.pm.is_installed("A", "1.0"))
        self.assertFalse(self.pm.is_installed("B", "2.0"))

    def test_lockfile_generation(self):
        """Test generating and installing from lockfiles"""
        # Create and use test environment
        self.pm.create_env("test_env")
        self.pm.use_env("test_env")
        
        # Install packages with dependencies
        self.pm.add_to_registry("A", "1.0", [])
        self.pm.add_to_registry("B", "2.0", ["A==1.0"])
        self.pm.install("B==2.0")
        
        # Generate lockfile
        lockfile_path = self.pm.generate_lockfile("test_env")
        self.assertTrue(os.path.exists(lockfile_path))
        
        # Verify lockfile content
        with open(lockfile_path) as f:
            lockfile = json.load(f)
        self.assertIn("A", lockfile)
        self.assertEqual(lockfile["A"], "1.0")
        self.assertIn("B", lockfile)
        self.assertEqual(lockfile["B"], "2.0")
        
        # Create a new environment and install from lockfile
        self.pm.create_env("dev_env")
        self.pm.use_env("dev_env")
        self.pm.install_from_lockfile(lockfile_path)
        
        # Verify packages were installed
        self.assertTrue(self.pm.is_installed("A", "1.0"))
        self.assertTrue(self.pm.is_installed("B", "2.0"))

    def test_find_package(self):
        """Test finding packages in the registry"""
        # Add packages to registry
        self.pm.add_to_registry("A", "1.0", [])
        self.pm.add_to_registry("A", "1.5", [])
        self.pm.add_to_registry("A", "2.0", [])
        
        # Find package with a version spec
        results = self.pm.find_package("A", ">=1.5")
        self.assertEqual(len(results), 2)
        self.assertIn(("A", "1.5"), results)
        self.assertIn(("A", "2.0"), results)
        
        # Find package with another spec
        results = self.pm.find_package("A", "<2.0")
        self.assertEqual(len(results), 2)
        self.assertIn(("A", "1.0"), results)
        self.assertIn(("A", "1.5"), results)

    def test_why_package(self):
        """Test finding why a package was installed"""
        # Set up registry with the packages we need
        self.pm.add_to_registry("A", "1.0", ["B==1.0", "C==1.0"])
        self.pm.add_to_registry("B", "1.0", ["D==1.0"])
        self.pm.add_to_registry("C", "1.0", [])
        self.pm.add_to_registry("D", "1.0", [])
        
        # Create a dependency chain
        self.pm.install("A==1.0")
        
        # Check why packages were installed
        reason = self.pm.why("A")
        self.assertEqual(reason, "direct install")
        
        reason = self.pm.why("B")
        self.assertEqual(reason, "dependency of A==1.0")
        
        reason = self.pm.why("D")
        self.assertEqual(reason, "dependency of B==1.0")


if __name__ == "__main__":
    unittest.main()