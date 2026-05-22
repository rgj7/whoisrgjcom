import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MoreHorizontalIcon,
  PencilIcon,
  TrashIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
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
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { deleteAdminPost, updateAdminPost, useAdminPosts } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

const PAGE_SIZE = 10;

export function PostsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading, error, mutate } = useAdminPosts(page, PAGE_SIZE);

  const handleDelete = async () => {
    if (!deleteId) return;
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      await deleteAdminPost(token, deleteId);
      await mutate();
    } catch {
      // TODO: show error toast
    }
    setDeleteId(null);
  };

  const totalPages = data?.pages ?? 0;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Posts</h1>
        <Button onClick={() => navigate("/dashboard/posts/new")}>
          New Post
        </Button>
      </div>

      {error && (
        <p className="text-sm text-red-500">{error.message}</p>
      )}

      {!error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead className="w-48">Date</TableHead>
                <TableHead className="w-32">Status</TableHead>
                <TableHead className="w-20">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Skeleton className="h-4 w-48" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-40" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-20" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-4" />
                    </TableCell>
                  </TableRow>
                ))
              ) : data?.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    No posts yet.
                  </TableCell>
                </TableRow>
              ) : (
                data?.items.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell>
                      <Link
                        to={`/posts/${post.slug}`}
                        className="hover:underline"
                      >
                        {post.title}
                      </Link>
                    </TableCell>
                    <TableCell className="w-48 whitespace-nowrap text-muted-foreground">
                      {new Date(post.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="w-32">
                      <Badge
                        variant={post.published ? "default" : "secondary"}
                        className="cursor-pointer"
                        onClick={() => {
                          const token = localStorage.getItem("token");
                          if (!token) return;
                          // Toggle published status
                          const newStatus = !post.published;
                          updateAdminPost(token, post.id, { published: newStatus })
                            .then(() => mutate())
                            .catch(() => {
                              // TODO: show error toast
                            });
                        }}
                      >
                        {post.published ? "Published" : "Unpublished"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontalIcon />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() =>
                              navigate(`/dashboard/posts/${post.id}/edit`)
                            }
                          >
                            <PencilIcon className="mr-2 size-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => setDeleteId(post.id)}
                          >
                            <TrashIcon className="mr-2 size-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {totalPages > 1 && (
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  {page > 1 ? (
                    <PaginationPrevious
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                    />
                  ) : (
                    <span className="pointer-events-none opacity-50">
                      <PaginationPrevious />
                    </span>
                  )}
                </PaginationItem>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                  (p) => (
                    <PaginationItem key={p}>
                      <PaginationLink
                        onClick={() => setPage(p)}
                        isActive={p === page}
                      >
                        {p}
                      </PaginationLink>
                    </PaginationItem>
                  )
                )}
                <PaginationItem>
                  {page < totalPages ? (
                    <PaginationNext
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    />
                  ) : (
                    <span className="pointer-events-none opacity-50">
                      <PaginationNext />
                    </span>
                  )}
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          )}
        </>
      )}

      <AlertDialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete post</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the post.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default PostsPage;
