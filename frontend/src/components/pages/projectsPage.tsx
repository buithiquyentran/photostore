import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  Eye,
  EyeOff,
  RefreshCw,
  Pencil,
  Trash2,
  Plus,
  LeafyGreen,
  Copy,
} from "lucide-react";
import ApiBaseVariable from "@/components/ui/ApiBaseVariable";
import ProjectsService from "@/components/api/projects.service";
interface Project {
  id: string;
  name: string;
  slug?: string;
  api_key: string;
  api_secret: string;
  description: string;
  created_at: string
}

export default function ProjectsPage() {
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>();

  useEffect(() => {
    const fetchData = async () => {
      const response = await ProjectsService.GetAll();
      setProjects(response);
    };
    fetchData();
  }, []);
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set());
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isRegenerateDialogOpen, setIsRegenerateDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState({ name: "", description: "" });

  const toggleSecretVisibility = (projectId: string) => {
    setVisibleSecrets((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(projectId)) {
        newSet.delete(projectId);
      } else {
        newSet.add(projectId);
      }
      return newSet;
    });
  };

  const generateSlug = (name: string) => {
    return name;
  };

  const handleNameChange = (name: string) => {
    setFormData({
      name,
      description: generateSlug(name),
    });
  };

  const handleCreateProject = () => {
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Project name is required",
        variant: "destructive",
      });
      return;
    }

    const newProject: Project = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      api_key: `sk_live_${Math.random().toString(36).substring(2, 18)}`,
      api_secret: `sk_secret_${Math.random().toString(36).substring(2, 42)}`,
    };

    setProjects([...(projects ? projects : []), newProject]);
    setIsCreateDialogOpen(false);
    setFormData({ name: "", description: "" });
    toast({
      title: "Success",
      description: "Project created successfully",
    });
  };

  const handleEditProject = () => {
    if (!selectedProject || !formData.name.trim()) {
      toast({
        title: "Error",
        description: "Project name is required",
        variant: "destructive",
      });
      return;
    }

    setProjects(
      projects?.map((p) =>
        p.id === selectedProject.id
          ? { ...p, name: formData.name, description: formData.description }
          : p
      )
    );
    setIsEditDialogOpen(false);
    setSelectedProject(null);
    setFormData({ name: "", description: "" });
    toast({
      title: "Success",
      description: "Project updated successfully",
    });
  };

  const handleDeleteProject = () => {
    if (!selectedProject) return;

    setProjects(projects?.filter((p) => p.id !== selectedProject.id));
    setIsDeleteDialogOpen(false);
    setSelectedProject(null);
    toast({
      title: "Success",
      description: "Project deleted successfully",
    });
  };

  const handleRegenerateSecret = () => {
    if (!selectedProject) return;

    setProjects(
      projects?.map((p) =>
        p.id === selectedProject.id
          ? {
              ...p,
              secretKey: `sk_secret_${Math.random()
                .toString(36)
                .substring(2, 42)}`,
            }
          : p
      )
    );
    setIsRegenerateDialogOpen(false);
    setSelectedProject(null);
    toast({
      title: "Success",
      description: "Secret key regenerated successfully",
    });
  };

  const openEditDialog = (project: Project) => {
    setSelectedProject(project);
    setFormData({ name: project.name, slug: project.slug });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (project: Project) => {
    setSelectedProject(project);
    setIsDeleteDialogOpen(true);
  };

  const openRegenerateDialog = (project: Project) => {
    setSelectedProject(project);
    setIsRegenerateDialogOpen(true);
  };

  const maskApiKey = (key: string) => {
    if (key.length <= 8) return key;
    return `${key.substring(0, 8)}****${key.substring(key.length - 4)}`;
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(date);
  };

  const [copied, setCopied] = useState(false);
  const handleCopy = async (item: string) => {
    try {
      await navigator.clipboard.writeText(item);
      setCopied(true);
      toast({ title: "Copied to clipboard!" });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };
  return (
    <div className="min-h-screen bg-[#000]">
      <div className="mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-balance text-3xl font-semibold tracking-tight text-foreground">
              Projects
            </h1>
            <p className="mt-2 text-pretty text-base">
              Manage API key and secret pairs for your product environment. To
              build the environment variable for each pair, copy the provided
              format and substitute your actual values for the placeholders.
              Make sure to store your secrets securely.
            </p>
            <ApiBaseVariable />
          </div>
          <Button
            size="lg"
            onClick={() => setIsCreateDialogOpen(true)}
            className="gap-2 text-[#000] text-lg"
          >
            <Plus className="h-4 w-4" />
            Create Project
          </Button>
        </div>

        <div className="rounded-lg border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent ">
                <TableHead className="font-semibold text-white text-xl">
                  Name
                </TableHead>
                <TableHead className="font-semibold text-white text-xl">
                  Slug
                </TableHead>
                <TableHead className="font-semibold text-white text-xl">
                  Created At
                </TableHead>
                <TableHead className="font-semibold text-white text-xl">
                  API Key
                </TableHead>
                <TableHead className="font-semibold text-white text-xl">
                  Secret Key
                </TableHead>
                <TableHead className="text-right font-semibold text-white text-xl">
                  Actions
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-32 text-center">
                    <p className="text-muted-foreground">
                      No projects yet. Create your first project to get started.
                    </p>
                  </TableCell>
                </TableRow>
              ) : (
                projects?.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">
                      {project.name}
                    </TableCell>
                    <TableCell className="font-mono text-base ">
                      {project.slug}
                    </TableCell>
                    <TableCell className="">{project.created_at}</TableCell>
                    <TableCell className="font-mono text-base">
                      {project.api_key}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleCopy(project.api_key)}
                        className="ml-3 hover:bg-gray-800"
                        title="Copy"
                      >
                        <Copy
                          className={`h-4 w-4 ${
                            copied ? "text-green-400" : "text-gray-400"
                          }`}
                        />
                      </Button>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <code className="rounded  px-2 py-1 font-mono text-base">
                          {visibleSecrets.has(project.id)
                            ? project.api_secret
                            : "•••••••••••••••••••••••••••••"}
                        </code>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => toggleSecretVisibility(project.id)}
                        >
                          {visibleSecrets.has(project.id) ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => openRegenerateDialog(project)}
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => openEditDialog(project)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          onClick={() => openDeleteDialog(project)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog
        open={isCreateDialogOpen || isEditDialogOpen}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false);
            setIsEditDialogOpen(false);
            setFormData({ name: "", description: "" });
            setSelectedProject(null);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {isCreateDialogOpen ? "Create Project" : "Edit Project"}
            </DialogTitle>
            <DialogDescription>
              {isCreateDialogOpen
                ? "Add a new project to manage your API credentials."
                : "Update your project details."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="My Project"
                value={formData.name}
                onChange={(e) => handleNameChange(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slug">Description</Label>
              <Input
                id="slug"
                placeholder="Describe your project"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateDialogOpen(false);
                setIsEditDialogOpen(false);
                setFormData({ name: "", description: "" });
                setSelectedProject(null);
              }}
            >
              Cancel
            </Button>
            <Button
              className="text-black"
              onClick={
                isCreateDialogOpen ? handleCreateProject : handleEditProject
              }
            >
              {isCreateDialogOpen ? "Create" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              project &quot;{selectedProject?.name}&quot; and remove all
              associated API credentials.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteProject}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Regenerate Secret Key Confirmation Dialog */}
      <AlertDialog
        open={isRegenerateDialogOpen}
        onOpenChange={setIsRegenerateDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Regenerate Secret Key?</AlertDialogTitle>
            <AlertDialogDescription>
              This will generate a new secret key for &quot;
              {selectedProject?.name}&quot;. The old key will be immediately
              invalidated and any applications using it will stop working.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRegenerateSecret}>
              Regenerate
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
